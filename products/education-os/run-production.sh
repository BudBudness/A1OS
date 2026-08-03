#!/data/data/com.termux/files/usr/bin/bash

set -e

cd ~/A1OS_RESTORED/products/education-os

export $(cat .env.production | xargs)

exec python3 -m uvicorn api.app:app \
 --host 127.0.0.1 \
 --port 3012 \
 --workers 1 \
 --proxy-headers
