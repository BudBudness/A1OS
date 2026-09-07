#!/usr/bin/env bash
set -euo pipefail

# A1OS System Storage Optimization Framework
ROOT_DIR="$HOME/A1OS_RESTORED"
DATA_DIR="$ROOT_DIR/data"

usage() {
    echo "Usage: $0 {audit|clean|purge-backups|all}"
    exit 1
}

system_audit() {
    echo -e "\n\033[1;34m=== SYSTEM WORKSPACE STORAGE AUDIT ===\033[0m"
    du -sh "$HOME"/* "$ROOT_DIR"/* 2>/dev/null | sort -rh | head -n 12
    echo -e "\n\033[1;34m=== HARDWARE DISK SPACE ALLOCATION ===\033[0m"
    df -h /data
}

system_clean() {
    echo -e "\n\033[1;33m[*] Initiating Canonical Maintenance Pipeline...\033[0m"
    
    # Clear native apt and pkg transaction caches safely
    echo "[+] Purging package management transaction data..."
    apt-get clean -y 2>/dev/null || true
    rm -rf "$PREFIX/var/cache/apt/archives"/* 2>/dev/null || true

    # Truncate real-time engine logging outputs without breaking active stream routing
    echo "[+] Shaving operational data stream logging footprints..."
    if [ -d "$DATA_DIR" ]; then
        find "$DATA_DIR" -type f -name "*.log" -exec truncate -s 0 {} +
    fi

    # Eradicate cached compiled bytecode layers globally across environments
    echo "[+] Evicting loose Python __pycache__ artifacts..."
    find "$HOME" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$HOME" -type f -name "*.pyc" -delete 2>/dev/null || true

    # Clear volatile transient runtime environment cache indices
    echo "[+] Emptying runtime user cache layers..."
    rm -rf "$HOME/.cache"/* 2>/dev/null || true
    
    echo -e "\033[1;32m[+] Canonical cleanup completed successfully.\033[0m"
}

purge_backups() {
    echo -e "\n\033[1;31m[*] Auditing Redundant Historical Workspace Archives...\033[0m"
    # Keep only the single most recent compressed baseline backup file to protect disaster recovery pathing
    local backup_count
    backup_count=$(find "$HOME" -maxdepth 1 -type f -name "a1os_backup_*.tar.gz" | wc -l)
    if [ "$backup_count" -gt 1 ]; then
        echo "[+] Consolidation required. Pruning stale backup structures..."
        ls -t "$HOME"/a1os_backup_*.tar.gz | tail -n +2 | xargs rm -f
        echo "[+] Stale compressed archives successfully cleared."
    else
        echo "[+] Archival space optimized. No duplicate tarball layers detected."
    fi
}

[ $# -eq 0 ] && usage

case "$1" in
    audit)          system_audit ;;
    clean)          system_clean ;;
    purge-backups)  purge_backups ;;
    all)            system_clean; purge_backups; system_audit ;;
    *)              usage ;;
esac
