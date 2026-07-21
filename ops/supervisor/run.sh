#!/bin/bash
BASE="/data/data/com.termux/files/home/A1OS"
while true; do
    # Run Strategy
    python3 -c "from company.ceo.strategy import CEO; from applications.executive_dashboard.monitor import get_org_status; c = CEO('Alpha', 'CEO', 'EXEC'); t = c.run_strategy(get_org_status()); t.save() if t else None"
    # Execute & Self-Heal
    python3 "$BASE/core/execution/framework.py"
    # System Pulse
    python3 "$BASE/core/monitor.py"
    sleep 30
done
