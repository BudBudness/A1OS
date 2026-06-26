#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p logs
echo "🚀 Starting A1OS..."
pkill -f "python3 api/server_full.py" 2>/dev/null
nohup python3 api/server_full.py > logs/server.log 2>&1 &
sleep 2
echo "✅ Backend: http://localhost:8086"
curl -s http://localhost:8086/ | python3 -m json.tool