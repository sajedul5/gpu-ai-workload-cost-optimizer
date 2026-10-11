#!/usr/bin/env bash
# PostToolUse hook (Edit|Write): format and validate the file Claude just changed.
# Each step is skipped when its tool is not installed.
# Exit code 2 sends the error back to Claude so it fixes the file.
set -uo pipefail

file=$(jq -r '.tool_input.file_path // ""')
[[ -z "$file" || ! -f "$file" ]] && exit 0

have() { command -v "$1" >/dev/null 2>&1; }
fail() { echo "$1" >&2; exit 2; }

case "$file" in
  *.tf)
    have terraform && terraform fmt "$file" >/dev/null
    ;;
  */k8s/*.yaml | */k8s/*.yml)
    if have kubeconform; then
      out=$(kubeconform -strict -ignore-missing-schemas -summary "$file" 2>&1) || fail "$out"
    fi
    ;;
  *.yaml | *.yml)
    if have yamllint; then
      out=$(yamllint -d relaxed "$file" 2>&1) || fail "$out"
    fi
    ;;
  *.json)
    out=$(jq empty "$file" 2>&1) || fail "Invalid JSON in $file: $out"
    ;;
  *.sh)
    if have shellcheck; then
      out=$(shellcheck "$file" 2>&1) || fail "$out"
    fi
    ;;
esac
exit 0
