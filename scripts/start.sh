#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p data logs
echo "🚀 Starting A1OS..."
pkill -f "python3 api/server.py" 2>/dev/null
pkill -f "http.server 8000" 2>/dev/null
nohup python3 api/server.py > logs/server.log 2>&1 &
sleep 3
cd ui/pwa && nohup python3 -m http.server 8000 > /dev/null 2>&1 &
echo "✅ Backend: http://localhost:8086"
echo "✅ PWA: http://localhost:8000"
curl -s http://localhost:8086/ | python3 -m json.tool
