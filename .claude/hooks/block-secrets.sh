#!/usr/bin/env bash
# PreToolUse hook (Edit|Write): keep secrets and real AWS identifiers out of this public repo.
# Exit code 2 blocks the write and shows stderr to Claude.
set -euo pipefail

content=$(jq -r '(.tool_input.content // "") + "\n" + (.tool_input.new_string // "")')

if grep -Eq 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' <<<"$content"; then
  echo "Blocked: content looks like an AWS access key or private key. This repo is public." >&2
  exit 2
fi

# 12-digit account IDs in ARNs or SQS/ECR URLs, except the documented placeholder.
ids=$(grep -Eo '(arn:aws[a-z-]*:[a-z0-9-]+:[a-z0-9-]*:|amazonaws\.com/|^|[^0-9])[0-9]{12}([^0-9]|$)' <<<"$content" \
  | grep -Eo '[0-9]{12}' | grep -v '^123456789012$' || true)
if [[ -n "$ids" ]] && grep -Eq '(arn:aws|amazonaws\.com)' <<<"$content"; then
  echo "Blocked: real-looking AWS account ID ($(head -1 <<<"$ids")). Use 123456789012 in examples." >&2
  exit 2
fi
exit 0
