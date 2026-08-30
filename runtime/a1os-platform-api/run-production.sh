#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD"
exec python3 - <<'PY'
import importlib.util
import uvicorn

APP = "platform/a1os-platform-api/api/app.py"
spec = importlib.util.spec_from_file_location("a1os_production_api", APP)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

if not hasattr(module, "app"):
    raise RuntimeError("FastAPI app object not found")

uvicorn.run(
    module.app,
    host="127.0.0.1",
    port=3013,
    workers=1,
    proxy_headers=True,
)
PY
