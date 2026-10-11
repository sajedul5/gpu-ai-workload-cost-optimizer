#!/usr/bin/env bash
# PreToolUse hook (Bash): block commands that change real infrastructure or rewrite history.
# Exit code 2 blocks the call and shows stderr to Claude.
set -euo pipefail

cmd=$(jq -r '.tool_input.command // ""')

patterns=(
  'terraform[[:space:]]+(apply|destroy|import|state[[:space:]]+(rm|mv|push))'
  'kubectl[[:space:]]+(delete|drain|cordon)'
  'helm[[:space:]]+(uninstall|delete|rollback)'
  'aws[[:space:]].*[[:space:]](delete-|terminate-|remove-)'
  'eksctl[[:space:]]+delete'
  'rm[[:space:]]+-rf[[:space:]]+(/|~|\$HOME)([[:space:]]|$)'
  'git[[:space:]]+push[[:space:]].*(--force|-f([[:space:]]|$))'
)

for p in "${patterns[@]}"; do
  if [[ "$cmd" =~ $p ]]; then
    echo "Blocked by project hook: this command changes real infrastructure or git history. Give the user the command to run themselves." >&2
    exit 2
  fi
done
exit 0
