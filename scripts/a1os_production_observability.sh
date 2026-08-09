#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
PRIMARY="${A1OS_PRIMARY_PORT:-3011}"
SECONDARY="${A1OS_SECONDARY_PORT:-3012}"
STATE="$ROOT/state"
LOGS="$ROOT/logs"
BACKUP="$ROOT/backups/external"
IMMUTABLE="$ROOT/backups/immutable"
STATUS="$STATE/production-observability.status"
ALERT="$STATE/production-alerts.log"

mkdir -p "$STATE" "$LOGS" "$BACKUP" "$IMMUTABLE"
chmod 700 "$IMMUTABLE"

timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

health() {
    curl --max-time 5 --silent --fail \
        "http://127.0.0.1:$1/v1/health" >/dev/null 2>&1
}

write_status() {
    local primary="$1"
    local secondary="$2"
    local replication="$3"
    local backup="$4"
    local secret="$5"

    cat > "$STATUS" <<EOF
TIMESTAMP=$(timestamp)
PRIMARY=$primary
SECONDARY=$secondary
REPLICATION=$replication
EXTERNAL_BACKUP=$backup
SECRET_LIFECYCLE=$secret
EOF
}

PRIMARY_STATUS=FAIL
SECONDARY_STATUS=FAIL
REPLICATION_STATUS=FAIL
BACKUP_STATUS=FAIL
SECRET_STATUS=FAIL

health "$PRIMARY" && PRIMARY_STATUS=PASS || true
health "$SECONDARY" && SECONDARY_STATUS=PASS || true

if [ -f "$STATE/replication-status" ] &&
   grep -q '^STATUS=healthy' "$STATE/replication-status"; then
    REPLICATION_STATUS=PASS
fi

if [ -f "$STATE/external-replication-status" ]; then
    BACKUP="$(grep '^EXTERNAL_BACKUP=' "$STATE/external-replication-status" | cut -d= -f2- || true)"
    if [ -n "$BACKUP" ] && [ -s "$BACKUP" ] && [ -s "$BACKUP.sha256" ]; then
        sha256sum -c "$BACKUP.sha256" >/dev/null 2>&1 && BACKUP_STATUS=PASS || true
    fi
fi

if [ -f "$STATE/../secrets/active" ]; then
    ACTIVE="$(cat "$STATE/../secrets/active")"
    [ -s "$STATE/../secrets/versions/${ACTIVE}.secret" ] && SECRET_STATUS=PASS || true
fi

write_status \
    "$PRIMARY_STATUS" \
    "$SECONDARY_STATUS" \
    "$REPLICATION_STATUS" \
    "$BACKUP_STATUS" \
    "$SECRET_STATUS"

if [ "$PRIMARY_STATUS" != PASS ] ||
   [ "$SECONDARY_STATUS" != PASS ] ||
   [ "$REPLICATION_STATUS" != PASS ] ||
   [ "$BACKUP_STATUS" != PASS ] ||
   [ "$SECRET_STATUS" != PASS ]; then
    printf '[%s] ALERT PRIMARY=%s SECONDARY=%s REPLICATION=%s BACKUP=%s SECRET=%s\n' \
        "$(timestamp)" \
        "$PRIMARY_STATUS" \
        "$SECONDARY_STATUS" \
        "$REPLICATION_STATUS" \
        "$BACKUP_STATUS" \
        "$SECRET_STATUS" >> "$ALERT"
    exit 1
fi

exit 0
