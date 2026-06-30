import os
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
print("BOOTSTRAP EXECUTING:", __file__)

DIRS = [
    "config",
    "build/generated/nodes",
    "generators",
    "ui/pwa",
    "logs"
]

for d in DIRS:
    (ROOT / d).mkdir(parents=True, exist_ok=True)

(ROOT / "generators").mkdir(parents=True, exist_ok=True)
(ROOT / "config").mkdir(parents=True, exist_ok=True)

(ROOT / "config/settings.json").write_text(
    '{"app_name": "A1OS", "version": "1.0.0"}'
)

(ROOT / "generators/__init__.py").touch()

print("✅ Generation complete")
