#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

export HOME=/data/data/com.termux/files/home
export PATH=/data/data/com.termux/files/usr/bin:$PATH

BACKUP_REPO="$HOME/a1os-backups"
PLATFORM_BACKUPS="$HOME/A1OS_RESTORED/products/a1os-platform-api/deployments/a1os-platform/backups"
STAGING="$BACKUP_REPO/a1os-platform"
REMOTE="https://github.com/BudBudness/a1os-backups.git"

latest="$(find "$PLATFORM_BACKUPS" -maxdepth 1 -type f -name 'a1os-platform-*.db' -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)"
if [ -z "$latest" ]; then
    echo "no backup files found in $PLATFORM_BACKUPS"
    exit 1
fi

mkdir -p "$STAGING"
cp "$latest" "$STAGING/a1os-platform-latest.db"
chmod 600 "$STAGING/a1os-platform-latest.db"

cd "$BACKUP_REPO"
if [ -z "$(git status --porcelain)" ]; then
    echo "no changes; already synced"
    exit 0
fi

git add -A
git commit -m "backup $(basename "$latest")"
git push origin main
echo "pushed $(basename "$latest") to $REMOTE"
