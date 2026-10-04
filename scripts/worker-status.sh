#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

load_required_var() {
  local name="$1"
  local value
  value="$(sed -n "s/^${name}=//p" .env.local | head -n 1)"
  if [[ -z "$value" ]]; then
    printf 'Missing %s in .env.local\n' "$name" >&2
    exit 1
  fi
  printf -v "$name" '%s' "$value"
  export "$name"
}

load_required_var SUPABASE_URL
load_required_var SUPABASE_SECRET_KEY

curl --fail --silent --show-error \
  "${SUPABASE_URL}/rest/v1/a1os_tasks?select=status&limit=1000" \
  -H "apikey: ${SUPABASE_SECRET_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SECRET_KEY}" |
python3 -c '
import json, sys
rows = json.load(sys.stdin)
counts = {}
for row in rows:
    status = row.get("status", "unknown")
    counts[status] = counts.get(status, 0) + 1
print(json.dumps({"tasks_sampled": len(rows), "status_counts": dict(sorted(counts.items()))}, sort_keys=True))
'
