#!/bin/bash
cd "$(dirname "$0")/../pwa"
while true; do
    python3 -m http.server 8000
    sleep 2
done
