
from fastapi import APIRouter
router=APIRouter(prefix="/v1/system",tags=["system"])

@router.get("/status")
def status():
    return {
        "system":"operational",
        "version":"3.5",
        "database":"connected",
        "production":"ready"
    }
