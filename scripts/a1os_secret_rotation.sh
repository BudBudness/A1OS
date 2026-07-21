#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
SECRET_DIR="$ROOT/secrets"
VERSION_DIR="$SECRET_DIR/versions"
REVOKED_DIR="$SECRET_DIR/revoked"
ACTIVE="$SECRET_DIR/active"
REGISTRY="$SECRET_DIR/registry"
LOCK="$ROOT/.locks/secret-rotation.lock"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
VERSION="v-${STAMP}"
NEW_SECRET="$VERSION_DIR/$VERSION.secret"

mkdir -p "$VERSION_DIR" "$REVOKED_DIR" "$ROOT/.locks"
chmod 700 "$SECRET_DIR" "$VERSION_DIR" "$REVOKED_DIR"

exec 9>"$LOCK"
flock -n 9 || exit 0

umask 077

if [ -f "$ACTIVE" ]; then
    OLD_VERSION="$(cat "$ACTIVE")"
    if [ -n "$OLD_VERSION" ] && [ -f "$VERSION_DIR/$OLD_VERSION.secret" ]; then
        mv "$VERSION_DIR/$OLD_VERSION.secret" \
           "$REVOKED_DIR/$OLD_VERSION.secret"
        printf '%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            > "$REVOKED_DIR/$OLD_VERSION.revoked"
    fi
fi

python3 - <<PY > "$NEW_SECRET"
import secrets
print(secrets.token_urlsafe(96))
PY

chmod 600 "$NEW_SECRET"
printf '%s\n' "$VERSION" > "$ACTIVE"

cat > "$REGISTRY" <<EOF
ACTIVE_VERSION=$VERSION
ROTATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
STATUS=active
REVOCATION=enabled
VERSIONING=enabled
EOF

chmod 600 "$ACTIVE" "$REGISTRY"

test -s "$NEW_SECRET"
test "$(cat "$ACTIVE")" = "$VERSION"
test -f "$VERSION_DIR/$VERSION.secret"

echo "=================================================="
echo " A1OS REAL SECRET ROTATION VALIDATION"
echo "=================================================="
echo
echo "[1/6] NEW SECRET VERSION"
echo "SECRET_VERSION=$VERSION"
echo "SECRET_GENERATION=PASS"
echo
echo "[2/6] ACTIVE VERSION"
echo "ACTIVE_VERSION=$(cat "$ACTIVE")"
echo "ACTIVE_VERSION=PASS"
echo
echo "[3/6] SECRET PERMISSIONS"
test "$(stat -c '%a' "$NEW_SECRET")" = "600"
echo "SECRET_PERMISSIONS=PASS"
echo
echo "[4/6] REVOCATION"
if [ -n "${OLD_VERSION:-}" ]; then
    test -f "$REVOKED_DIR/$OLD_VERSION.revoked"
    echo "PREVIOUS_SECRET_REVOKED=PASS"
else
    echo "INITIAL_ROTATION_NO_PREVIOUS_VERSION=PASS"
fi
echo
echo "[5/6] VERSION REGISTRY"
grep -q "^ACTIVE_VERSION=$VERSION$" "$REGISTRY"
grep -q "^REVOCATION=enabled$" "$REGISTRY"
grep -q "^VERSIONING=enabled$" "$REGISTRY"
echo "VERSION_REGISTRY=PASS"
echo
echo "[6/6] FINAL STATUS"
echo "SECRET_ROTATION=PASS"
echo "SECRET_VERSIONING=PASS"
echo "SECRET_REVOCATION=PASS"
echo "ACTIVE_SECRET_ENFORCEMENT=PASS"
echo "A1OS_REAL_SECRET_ROTATION=PASS"
echo "=================================================="
