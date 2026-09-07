#!/data/data/com.termux/files/usr/bin/sh

OLD_PID="$1"

sleep 1

if [ -n "$OLD_PID" ]; then
    kill -TERM "$OLD_PID" 2>/dev/null || true
fi

sleep 2

cd ~/A1OS_RESTORED || exit 1

export PYTHONPATH="$PWD"

nohup python3 -c '
import importlib.util, uvicorn
p="platform/a1os-platform-api/api/app.py"
s=importlib.util.spec_from_file_location("a1os_production_api", p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
uvicorn.run(
    m.app,
    host="127.0.0.1",
    port=3013,
    workers=1,
    proxy_headers=True
)
' > runtime/a1os-platform-api-3013.log 2>&1 &
