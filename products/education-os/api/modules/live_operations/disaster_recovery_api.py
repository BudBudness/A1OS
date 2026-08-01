
from fastapi import APIRouter
from pathlib import Path
import shutil
from datetime import datetime

router=APIRouter(prefix="/v1/recovery",tags=["recovery"])

DB=Path("deployments/little-oaks/data/education.db")
BACKUP=Path("deployments/little-oaks/backups")
BACKUP.mkdir(parents=True,exist_ok=True)

@router.get("/status")
def status():
    return {
        "recovery":"enabled",
        "backup_directory":str(BACKUP),
        "database":"available",
        "restore":"ready"
    }

@router.post("/backup")
def backup():
    if DB.exists():
        name=f"education_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        target=BACKUP/name
        shutil.copy(DB,target)
        return {"backup":"created","file":str(target)}
    return {"backup":"failed","reason":"database missing"}

@router.get("/backups")
def backups():
    return {
        "backups":[x.name for x in BACKUP.glob("*.db")]
    }
