
from fastapi import APIRouter
router=APIRouter(prefix="/v1/monitoring",tags=["monitoring"])

@router.get("/status")
def status():
    return {"monitoring":"active","metrics":"enabled","alerts":"enabled"}
