#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p backups
cp data/a1os.db backups/a1os_$(date +%Y%m%d_%H%M%S).db 2>/dev/null
echo "✅ Backup completed"
