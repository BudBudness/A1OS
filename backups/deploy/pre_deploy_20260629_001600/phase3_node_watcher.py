
import time, subprocess
from pathlib import Path
WATCH_DIR = Path("artifacts/raw_memory")
EMIT_DIR = Path("artifacts/vector_memory")
while True:
    for f in WATCH_DIR.glob("*"):
        if f.is_file():
            print(f"Processing: {f}")
            (EMIT_DIR / f.name).touch()
            f.unlink()
    time.sleep(1)
