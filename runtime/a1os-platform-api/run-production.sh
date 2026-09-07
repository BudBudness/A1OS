#!/data/data/com.termux/files/usr/bin/bash
set -e

# Hardened Parameter Enforcements
ROOT="/data/data/com.termux/files/home/A1OS_RESTORED"
export PYTHONPATH="$ROOT/platform/a1os-platform-api/api:$ROOT"
export A1OS_RUNTIME_ENV="production"
export A1OS_COOKIE_SECURE="true"
export A1OS_SERVICE_NAME="a1os-platform-api"

cd "$ROOT/platform/a1os-platform-api/api" || exit 1

# Force the execution strictly into foreground mode under the active package environment
exec "$ROOT/.venv-test/bin/python3" -m uvicorn app:app --host 127.0.0.1 --port 3013 --workers 4 --proxy-headers
