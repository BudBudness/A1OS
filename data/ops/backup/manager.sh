#!/bin/bash
# A1OS Automated Backup Manager
BACKUP_DIR="$HOME/A1OS/backups/ops"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Compress state directories
tar -czf "$BACKUP_DIR/state_$TIMESTAMP.tar.gz" -C "$HOME/A1OS" data/
echo "[$(date)] SUCCESS: State backup created at $BACKUP_DIR/state_$TIMESTAMP.tar.gz" >> "$HOME/A1OS/logs/ops/backup.log"
