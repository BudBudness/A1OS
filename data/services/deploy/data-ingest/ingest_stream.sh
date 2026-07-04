#!/bin/bash
# A1OS Universal Ingest Stream Handler
# Usage: <stream_data> | ./ingest_stream.sh <category>

CATEGORY=${1:-"misc"}
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
DATA_FILE="$HOME/A1OS/data/ingest/catalog/$CATEGORY/$TIMESTAMP.jsonl"
AUDIT_LOG="$HOME/A1OS/data/ingest/logs/audit.jsonl"

mkdir -p "$(dirname "$DATA_FILE")"
mkdir -p "$(dirname "$AUDIT_LOG")"

# Save stream and generate metadata
cat - > "$DATA_FILE"
echo "{\"timestamp\": \"$TIMESTAMP\", \"category\": \"$CATEGORY\", \"file\": \"$DATA_FILE\", \"hash\": \"$(sha256sum "$DATA_FILE" | cut -d' ' -f1)\"}" >> "$AUDIT_LOG"
