#!/bin/bash
METRIC_LOG="$HOME/A1OS/logs/ops/metrics.log"
# Get memory via procmeminfo or free if available; get cpu load via uptime
MEM=$(grep MemTotal /proc/meminfo | awk '{print $2/1024 "MB"}')
CPU=$(uptime | awk -F'load average:' '{ print $2 }')
echo "[$(date +%s)] MEM: $MEM | LOAD: $CPU" >> "$METRIC_LOG"
