
import os, shutil
from pathlib import Path
BUILD_ROOT = Path("build/generated")
for module in schema.get("modules", {}):
    (BUILD_ROOT / module).mkdir(parents=True, exist_ok=True)
print("✅ Full build structure created")
