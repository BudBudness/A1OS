#!/bin/bash
CATEGORY="$1"
MAX_AGE="$2"
TARGET_DIR="$HOME/A1OS/data/ingest/catalog/$CATEGORY"

LAST_FILE=$(find "$TARGET_DIR" -maxdepth 1 -name "*.jsonl" -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")

if [ -z "$LAST_FILE" ]; then
    echo "{\"timestamp\": \"$(date +%Y-%m-%d_%H%M%S)\", \"event\": \"HEALTH_ALERT\", \"category\": \"$CATEGORY\", \"status\": \"no_data\"}" >> "$HOME/A1OS/data/ingest/logs/audit.jsonl"
    exit 1
fi

FILE_TIME=$(stat -c %Y "$LAST_FILE")
CURRENT_TIME=$(date +%s)

if [ $((CURRENT_TIME - FILE_TIME)) -gt "$MAX_AGE" ]; then
    echo "{\"timestamp\": \"$(date +%Y-%m-%d_%H%M%S)\", \"event\": \"HEALTH_ALERT\", \"category\": \"$CATEGORY\", \"status\": \"stale\"}" >> "$HOME/A1OS/data/ingest/logs/audit.jsonl"
else
    echo "{\"timestamp\": \"$(date +%Y-%m-%d_%H%M%S)\", \"event\": \"HEALTH_OK\", \"category\": \"$CATEGORY\", \"status\": \"active\"}" >> "$HOME/A1OS/data/ingest/logs/audit.jsonl"
fi
