
from fastapi import APIRouter
from datetime import datetime
from pathlib import Path
import subprocess

router = APIRouter(prefix="/v1/release", tags=["release"])

ROOT = Path(".")
BACKUP = Path("deployments/little-oaks/backups")

@router.get("/status")
def status():
    return {
        "release":"v3.9",
        "environment":"production",
        "deployment":"Little Oaks Montessori Nursery & Kindergarten",
        "timestamp":datetime.utcnow().isoformat(),
        "status":"stable"
    }

@router.get("/manifest")
def manifest():
    files = [
        "api/app.py",
        "api/security_layer.py",
        "api/modules/live_operations",
        "deployments/little-oaks"
    ]

    return {
        "release":"v3.9",
        "components":files,
        "backup_count":len(list(BACKUP.glob("*.db"))) if BACKUP.exists() else 0
    }

@router.get("/git")
def git():
    try:
        commit=subprocess.check_output(
            ["git","log","-1","--oneline"],
            text=True
        ).strip()
    except Exception:
        commit="unknown"

    return {
        "latest_commit":commit
    }
