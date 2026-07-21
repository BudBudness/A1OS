#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
SECRETS="$ROOT/secrets"
VERSIONS="$SECRETS/versions"
CURRENT="$SECRETS/runtime.secret"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
NEW="$VERSIONS/runtime-${STAMP}.secret"

umask 077
python3 - <<'PY' > "$NEW"
import secrets
print(secrets.token_urlsafe(64))
PY

chmod 600 "$NEW"

if [ -f "$CURRENT" ]; then
    cp "$CURRENT" "$VERSIONS/runtime-revoked-${STAMP}.secret"
    chmod 600 "$VERSIONS/runtime-revoked-${STAMP}.secret"
fi

cp "$NEW" "$CURRENT"
printf '%s\n' "$STAMP" > "$SECRETS/current.version.id"
chmod 600 "$CURRENT" "$SECRETS/current.version.id"

echo "SECRET_ROTATION=PASS"
echo "SECRET_VERSION=$STAMP"
echo "PREVIOUS_SECRET=REVOKED"
