#!/bin/bash
while true; do
  curl -s http://localhost:8086/hardware/battery > /dev/null 2>&1
  curl -s http://localhost:8086/hardware/location > /dev/null 2>&1
  sleep 60
done
