#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/A1OS_RESTORED"
EDU="$ROOT/products/education-os"
API="$EDU/api/app.py"
LOG="$HOME/little-oaks-release.log"
RELEASE_DIR="$EDU/RELEASES"
BACKUP_DIR="$EDU/deployments/little-oaks/backups"
DB="$EDU/deployments/little-oaks/data/education.db"
PORT="${A1OS_PORT:-3012}"
BASE="http://127.0.0.1:$PORT"
EMAIL="${A1OS_TEST_EMAIL:-leticia@littleoaks.ug}"
PASSWORD="${A1OS_TEST_PASSWORD:-admin@123}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RELEASE="$RELEASE_DIR/$STAMP"

exec > >(tee -a "$LOG") 2>&1

pass() { printf 'PASS — %s\n' "$1"; }
fail() { printf 'FAIL — %s\n' "$1" >&2; exit 1; }

printf '%s\n' '============================================================'
printf '%s\n' 'LITTLE OAKS EDUCATION OS — MASTER RELEASE PIPELINE'
printf '%s\n' 'VERSION 1.0.0 → PRODUCTION + HYPERCARE INITIALIZATION'
printf '%s\n' '============================================================'

cd "$ROOT"

# 1. Repository integrity
test -f "$API" || fail "API source missing"
python3 -m py_compile "$API" || fail "API syntax failure"
git diff --check || fail "Git whitespace/integrity failure"
pass "repository integrity"

# 2. Required acceptance suites
for suite in \
  "$EDU/WORK/STAGE_4_PRODUCTION_UI_AND_WORKFLOWS/LIVE_ACCEPTANCE/stage_4_acceptance.py" \
  "$EDU/WORK/STAGE_5_DIRECTOR_INTELLIGENCE/LIVE_ACCEPTANCE/stage_5_acceptance.py" \
  "$EDU/WORK/STAGE_6_PRODUCTION_HARDENING/LIVE_ACCEPTANCE/stage_6_acceptance.py" \
  "$EDU/WORK/STAGE_7_PRODUCTION_LAUNCH/LIVE_ACCEPTANCE/stage_7_acceptance.py"
do
  test -f "$suite" || fail "missing acceptance suite: $suite"
done
pass "Stage 4–7 acceptance suites present"

# 3. Production backup
mkdir -p "$BACKUP_DIR" "$RELEASE_DIR" "$RELEASE"
test -f "$DB" || fail "production database missing"

BACKUP="$BACKUP_DIR/education-$STAMP.db"
sqlite3 "$DB" ".backup '$BACKUP'"
test -s "$BACKUP" || fail "database backup empty"
sqlite3 "$BACKUP" "PRAGMA integrity_check;" | grep -qx "ok" || fail "backup integrity failure"
pass "production database backup verified"

# 4. Release manifest
COMMIT="$(git rev-parse HEAD)"
cat > "$RELEASE/release-manifest.txt" <<MANIFEST
PRODUCT=Little Oaks Education OS
VERSION=1.0.0
RELEASE_TYPE=Production Release Candidate
RELEASE_TIMESTAMP_UTC=$STAMP
GIT_COMMIT=$COMMIT
DATABASE_BACKUP=$BACKUP
API_PORT=$PORT
MANIFEST
pass "release manifest created"

# 5. Start production API
pkill -f "uvicorn.*$PORT" 2>/dev/null || true
sleep 2

nohup sh -c \
  "cd '$EDU/api' && exec python3 -m uvicorn app:app --host 127.0.0.1 --port $PORT" \
  > "$HOME/a1os-uvicorn.log" 2>&1 < /dev/null &

sleep 4

curl -fsS "$BASE/v1/health" >/dev/null || {
  tail -n 80 "$HOME/a1os-uvicorn.log"
  fail "production API health failure"
}
pass "production API healthy"

# 6. Production authentication
TOKEN="$(
  curl -fsS -X POST "$BASE/auth/login" \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" |
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("access_token") or d.get("token") or "")'
)"

test -n "$TOKEN" || fail "production authentication failed"
pass "production authentication verified"

AUTH=(-H "Authorization: Bearer $TOKEN")

# 7. Operational route smoke test
for route in \
  /auth/me \
  /students \
  /parents \
  /attendance \
  /fees \
  /reports \
  /alerts \
  /intelligence/summary \
  /intelligence/insights
do
  STATUS="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" "$BASE$route")"
  [ "$STATUS" = "200" ] || fail "$route returned HTTP $STATUS"
  pass "production route $route"
done

# 8. Dashboard
STATUS="$(curl -sS -o /dev/null -w '%{http_code}' "$BASE/director-dashboard")"
[ "$STATUS" = "200" ] || fail "director dashboard returned HTTP $STATUS"
pass "production dashboard"

# 9. Full acceptance suites
export A1OS_BASE_URL="$BASE"
export A1OS_TEST_EMAIL="$EMAIL"
export A1OS_TEST_PASSWORD="$PASSWORD"

python3 "$EDU/WORK/STAGE_4_PRODUCTION_UI_AND_WORKFLOWS/LIVE_ACCEPTANCE/stage_4_acceptance.py"
python3 "$EDU/WORK/STAGE_5_DIRECTOR_INTELLIGENCE/LIVE_ACCEPTANCE/stage_5_acceptance.py"
python3 "$EDU/WORK/STAGE_6_PRODUCTION_HARDENING/LIVE_ACCEPTANCE/stage_6_acceptance.py"
python3 "$EDU/WORK/STAGE_7_PRODUCTION_LAUNCH/LIVE_ACCEPTANCE/stage_7_acceptance.py"

pass "full Stage 4–7 acceptance pipeline"

# 10. Create hypercare operating structure
mkdir -p \
  "$EDU/OPERATIONS/HYPERCARE_30_DAYS" \
  "$EDU/OPERATIONS/INCIDENTS" \
  "$EDU/OPERATIONS/FEEDBACK" \
  "$EDU/ROADMAP/V1.1_STABILIZATION" \
  "$EDU/ROADMAP/V1.5_AUTOMATION_AI" \
  "$EDU/ROADMAP/V2.0_PLATFORM"

cat > "$EDU/OPERATIONS/HYPERCARE_30_DAYS/README.md" <<'DOC'
# Little Oaks Education OS — 30-Day Hypercare

## Objectives
- Monitor production reliability
- Capture real staff feedback
- Track defects
- Verify backups
- Monitor authentication and API errors
- Validate school workflows against real operations

## Daily checks
- API health
- Authentication
- Database integrity
- Backup creation
- Error logs
- Student operations
- Attendance
- Fees
- Reports
- Alerts
- Director Intelligence

## Rule
Production observations drive V1.1 priorities.
DOC

cat > "$EDU/ROADMAP/V1.1_STABILIZATION/README.md" <<'DOC'
# Version 1.1 — Stabilization

Prioritize:
- Production defects
- Usability friction
- Performance bottlenecks
- Reporting improvements
- Data quality issues
- Staff workflow improvements
- Backup and recovery improvements
DOC

cat > "$EDU/ROADMAP/V1.5_AUTOMATION_AI/README.md" <<'DOC'
# Version 1.5 — Automation and Intelligence

Candidate capabilities:
- Automated fee reminders
- Parent communication workflows
- Attendance alerts
- Automated report generation
- Director daily briefing
- Risk detection
- Student performance trends
- Fee arrears intelligence
- Staff activity intelligence
DOC

cat > "$EDU/ROADMAP/V2.0_PLATFORM/README.md" <<'DOC'
# Version 2.0 — Little Oaks Education OS Platform

Candidate capabilities:
- Parent portal
- Teacher portal
- PWA/mobile experience
- Online admissions
- Digital report cards
- Payroll
- Inventory
- Transport
- Library
- Communications
- Multi-campus support
- Offline-first synchronization
DOC

# 11. Release tag
if ! git rev-parse v1.0.0 >/dev/null 2>&1; then
  git tag -a v1.0.0 -m "Little Oaks Education OS Version 1.0.0 production release"
fi

git add \
  little-oaks-release.sh \
  "$EDU/OPERATIONS" \
  "$EDU/ROADMAP" \
  "$EDU/RELEASES"

git commit -m "release: Little Oaks Education OS v1.0.0 production launch" || true

git push origin main
git push origin v1.0.0

printf '%s\n' '============================================================'
printf '%s\n' 'LITTLE OAKS EDUCATION OS — PRODUCTION LAUNCH COMPLETE'
printf '%s\n' '============================================================'
printf '%s\n' 'VERSION 1.0.0: RELEASED'
printf '%s\n' 'DATABASE BACKUP: VERIFIED'
printf '%s\n' 'PRODUCTION API: HEALTHY'
printf '%s\n' 'AUTHENTICATION: VERIFIED'
printf '%s\n' 'STAGE 4–7 ACCEPTANCE: PASS'
printf '%s\n' 'HYPERCARE: INITIALIZED'
printf '%s\n' 'V1.1 ROADMAP: INITIALIZED'
printf '%s\n' 'V1.5 AUTOMATION + AI ROADMAP: INITIALIZED'
printf '%s\n' 'V2.0 PLATFORM ROADMAP: INITIALIZED'
printf '%s\n' '============================================================'
printf '%s\n' 'LITTLE OAKS EDUCATION OS — VERSION 1.0.0 LIVE'
printf '%s\n' 'NEXT: 30-DAY HYPERCARE OPERATIONS'
printf '%s\n' '============================================================'
