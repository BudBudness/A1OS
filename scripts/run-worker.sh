#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

load_optional_var() {
  local name="$1"
  local value
  value="$(sed -n "s/^${name}=//p" .env.local 2>/dev/null | head -n 1)"
  if [[ -n "$value" ]]; then
    printf -v "$name" '%s' "$value"
    export "$name"
  fi
}

# Cloudflare D1 credentials are optional when intentionally running the local
# SQLite queue under Termux. If only one is supplied, the Python client fails closed.
load_optional_var A1OS_TASK_QUEUE_URL
load_optional_var A1OS_TASK_QUEUE_TOKEN

export A1OS_WORKER_POLL_SECONDS="${A1OS_WORKER_POLL_SECONDS:-2}"
export A1OS_WORKER_BATCH_SIZE="${A1OS_WORKER_BATCH_SIZE:-10}"
export A1OS_WORKER_STALE_SECONDS="${A1OS_WORKER_STALE_SECONDS:-300}"

stop_requested=0
trap 'stop_requested=1' INT TERM

while true; do
  if python3 -m core.worker; then
    exit_code=0
  else
    exit_code=$?
  fi

  if [[ "$stop_requested" == "1" ]]; then
    exit "$exit_code"
  fi

  printf 'A1OS worker exited with code %s; restarting in 3 seconds.\n' "$exit_code" >&2
  sleep 3
done
