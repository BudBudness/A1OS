#!/data/data/com.termux/files/usr/bin/bash

set -e

cd ~/A1OS_RESTORED/products/a1os-platform-api

exec python3 -m uvicorn api.app:app \
 --host 127.0.0.1 \
 --port 3013 \
 --workers 1 \
 --proxy-headers
