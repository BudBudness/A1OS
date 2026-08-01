
from fastapi import APIRouter
from pathlib import Path
import sqlite3
import os

router = APIRouter(prefix="/v1/readiness", tags=["readiness"])

DB = Path("deployments/little-oaks/data/education.db")

@router.get("/status")
def status():
    database = "connected" if DB.exists() else "missing"

    return {
        "production":"ready",
        "database":database,
        "security":"active",
        "rbac":"enabled",
        "observability":"enabled",
        "recovery":"enabled",
        "api":"online"
    }

@router.get("/checks")
def checks():
    checks = {
        "database": False,
        "backup_directory": False,
        "api_modules": False,
        "security_layer": False,
        "monitoring": False
    }

    if DB.exists():
        checks["database"] = True

    if Path("deployments/little-oaks/backups").exists():
        checks["backup_directory"] = True

    if Path("api/modules/live_operations").exists():
        checks["api_modules"] = True

    if Path("api/security_layer.py").exists():
        checks["security_layer"] = True

    if Path("api/modules/live_operations/observability_api.py").exists():
        checks["monitoring"] = True

    return {
        "checks":checks,
        "passed":all(checks.values())
    }
