#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/backups"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
sqlite3 "$ROOT/data/a1os.db" ".backup '$ROOT/backups/a1os-$STAMP.db'"
tar -czf "$ROOT/backups/a1os-$STAMP.tar.gz" \
    "$ROOT/data" \
    "$ROOT/migrations" \
    "$ROOT/config" 2>/dev/null || true

find "$ROOT/backups" -type f -mtime +14 -delete
echo "BACKUP_CREATED=$ROOT/backups/a1os-$STAMP.db"
