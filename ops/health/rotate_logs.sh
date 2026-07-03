#!/bin/bash
LOG_FILE="$HOME/A1OS/data/ingest/logs/audit.jsonl"
BACKUP_FILE="$HOME/A1OS/data/ingest/logs/audit.old.jsonl"

if [ -f "$LOG_FILE" ]; then
    # Keep the last 1000 lines
    tail -n 1000 "$LOG_FILE" > "$BACKUP_FILE"
    mv "$BACKUP_FILE" "$LOG_FILE"
fi
