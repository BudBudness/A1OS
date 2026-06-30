
import os, time, shutil
from pathlib import Path
QUEUE_ROOT = Path("queue")
for d in ["incoming", "processing", "complete", "failed", "retry", "archive"]:
    (QUEUE_ROOT / d).mkdir(parents=True, exist_ok=True)
print("✅ Queue directories created")
