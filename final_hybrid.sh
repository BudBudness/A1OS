#!/bin/bash
echo "🚀 A1OS FINAL HYBRID — EXECUTING"
pkill -f gunicorn ; pkill -f http.server ; screen -wipe
rm -f data/a1os.db
python3 -c "from complete_system import init_db; init_db();" 2>/dev/null
sqlite3 data/a1os.db "UPDATE agents SET metadata = '{}';" 2>/dev/null
sqlite3 data/a1os.db "UPDATE knowledge SET metadata = '{}';" 2>/dev/null
sqlite3 data/a1os.db "UPDATE scheduled_tasks SET metadata = '{}';" 2>/dev/null
sed -i '/register_hardware_routes(app)/d' complete_system.py 2>/dev/null
sed -i '/register_domain_routes(app)/a register_hardware_routes(app)' complete_system.py 2>/dev/null
screen -dmS backend gunicorn -w 2 -b 127.0.0.1:8086 complete_system:app
sleep 5
for agent in "Memory-Agent" "Knowledge-Agent" "Task-Agent" "Hardware-Agent" "System-Agent" "Analytics-Agent" "Backup-Agent" "Communication-Agent"; do
  curl -s -X POST http://localhost:8086/agents -H "X-API-Key: f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108" -H "Content-Type: application/json" -d "{\"name\":\"$agent\",\"type\":\"worker\"}" > /dev/null
done
cd ui/pwa && screen -dmS pwa python3 -m http.server 8000
cd ~/A1OS
sleep 3
curl -s http://localhost:8086/ | python3 -m json.tool
echo ""
echo "✅ A1OS Hybrid — You control strategy. Agents execute."
termux-open http://localhost:8000
