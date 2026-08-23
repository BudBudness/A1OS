#!/data/data/com.termux/files/usr/bin/bash
# A1OS managed runtime supervisor.
# WU-12 entrypoint: delegates service restarts to canonical adapters.

set -Eeuo pipefail

ROOT="$HOME/A1OS_RESTORED"

CORE_ADAPTER="$ROOT/ops/adapters/restart-core.sh"
PLATFORM_ADAPTER="$ROOT/ops/adapters/restart-platform-api.sh"

for adapter in "$CORE_ADAPTER" "$PLATFORM_ADAPTER"; do
    if [ ! -x "$adapter" ]; then
        echo "ERROR: missing or non-executable runtime adapter: $adapter" >&2
        exit 1
    fi
done

echo "A1OS runtime supervisor: restarting core"
"$CORE_ADAPTER"

echo "A1OS runtime supervisor: restarting platform-api"
"$PLATFORM_ADAPTER"

echo "A1OS runtime supervisor: restart sequence complete"
