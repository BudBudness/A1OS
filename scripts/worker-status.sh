#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

load_required_var() {
  local name="$1"
  local value
  value="$(sed -n "s/^${name}=//p" .env.local 2>/dev/null | head -n 1)"
  if [[ -z "$value" ]]; then
    printf 'Missing %s in .env.local\n' "$name" >&2
    exit 1
  fi
  printf -v "$name" '%s' "$value"
  export "$name"
}

load_required_var A1OS_TASK_QUEUE_URL
load_required_var A1OS_TASK_QUEUE_TOKEN

curl --fail --silent --show-error \
  "${A1OS_TASK_QUEUE_URL%/}/health" \
  -H "Authorization: Bearer ${A1OS_TASK_QUEUE_TOKEN}" |
python3 -c '
import json, sys
payload = json.load(sys.stdin)
if payload.get("ok") is not True or payload.get("service") != "a1os-d1-task-queue":
    raise SystemExit("Unexpected Cloudflare task queue health response")
print(json.dumps({"status": "healthy", "service": payload["service"]}, sort_keys=True))
'
