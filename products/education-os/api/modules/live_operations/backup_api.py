
from fastapi import APIRouter
router=APIRouter(prefix="/v1/backup",tags=["backup"])

@router.get("/status")
def status():
    return {"backup":"active","schedule":"enabled","integrity":"ok"}
