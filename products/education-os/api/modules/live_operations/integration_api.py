
from fastapi import APIRouter
router=APIRouter(prefix="/v1/integrations",tags=["integrations"])

@router.get("/status")
def status():
    return {"integrations":"active","services":"connected"}
