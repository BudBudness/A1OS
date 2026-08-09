#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
SEC="$ROOT/secrets"
STATE="$ROOT/state"
AUDIT="$ROOT/audit"
LOG="$ROOT/logs/a1os-security-enforcement.log"
LOCK="$ROOT/.locks/security-enforcement.lock"

mkdir -p "$AUDIT" "$ROOT/logs" "$ROOT/.locks"
chmod 700 "$AUDIT" "$ROOT/.locks"

exec 9>"$LOCK"
flock -n 9 || exit 0

ts() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

audit() {
    printf '[%s] %s\n' "$(ts)" "$*" >> "$LOG"
}

while true; do
    ACTIVE="$(cat "$SEC/active" 2>/dev/null || true)"

    if [ -z "$ACTIVE" ] ||
       [ ! -s "$SEC/versions/${ACTIVE}.secret" ]; then
        audit "SECURITY_ALERT active_secret_invalid"
        printf '%s\n' "SECURITY_STATUS=DEGRADED" > "$STATE/security-status"
    else
        HASH="$(sha256sum "$SEC/versions/${ACTIVE}.secret" | awk '{print $1}')"
        printf '%s\n' \
            "SECURITY_STATUS=healthy" \
            "ACTIVE_VERSION=$ACTIVE" \
            "ACTIVE_HASH=$HASH" \
            "LAST_CHECK=$(ts)" \
            > "$STATE/security-status"
        chmod 600 "$STATE/security-status"
        audit "SECRET_POLICY healthy version=$ACTIVE"
    fi

    if [ -f "$STATE/replication-status" ] &&
       grep -q '^STATUS=healthy' "$STATE/replication-status"; then
        audit "REPLICATION_POLICY healthy"
    else
        audit "SECURITY_ALERT replication_degraded"
    fi

    if [ -f "$STATE/external-replication-status" ]; then
        BACKUP="$(grep '^EXTERNAL_BACKUP=' "$STATE/external-replication-status" | cut -d= -f2- || true)"
        if [ -n "$BACKUP" ] && [ -s "$BACKUP" ] && [ -s "$BACKUP.sha256" ] &&
           sha256sum -c "$BACKUP.sha256" >/dev/null 2>&1; then
            audit "BACKUP_INTEGRITY healthy"
        else
            audit "SECURITY_ALERT backup_integrity_failed"
        fi
    fi

    sleep "${A1OS_SECURITY_INTERVAL:-60}"
done
