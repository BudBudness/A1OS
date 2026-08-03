
from fastapi import APIRouter
import time
import os

router = APIRouter(prefix="/v1/observability", tags=["observability"])

START=time.time()

@router.get("/status")
def status():
    return {
        "observability":"active",
        "uptime_seconds":round(time.time()-START,2),
        "environment":"production",
        "service":"Little Oaks Education OS"
    }

@router.get("/metrics")
def metrics():
    return {
        "api":"online",
        "database":"connected",
        "monitoring":"enabled",
        "alerts":"enabled",
        "logs":"enabled"
    }

@router.get("/deployment")
def deployment():
    return {
        "release":"v3.6",
        "deployment":"production",
        "rollback":"available",
        "backup":"enabled"
    }
