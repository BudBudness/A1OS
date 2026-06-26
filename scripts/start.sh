#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p logs data
echo "🚀 Starting A1OS v1.0..."
pkill -f "python3 api/server.py" 2>/dev/null
nohup python3 api/server.py > logs/server.log 2>&1 &
sleep 2
curl -s http://localhost:8086/ | python3 -m json.tool
