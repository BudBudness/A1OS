#!/bin/bash
while true; do
  clear
  echo "--- A1OS DASHBOARD ---"
  echo "Time: $(date)"
  echo "Active Tasks: $(ls data/tasks/active 2>/dev/null | wc -l)"
  echo -e "\n--- LOGS ---"
  tail -n 10 tunnel.log 2>/dev/null
  sleep 2
done
