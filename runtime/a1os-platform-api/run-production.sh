#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
API_DIR="$ROOT/.private/platform/a1os-platform-api/api"

cd "$API_DIR"
export PYTHONPATH="$API_DIR:$ROOT/.private:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export A1OS_PLATFORM_DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"

exec python3 -m uvicorn app:app \
    --host 127.0.0.1 \
    --port 3013 \
    --workers 1 \
    --proxy-headers
