from fastapi import APIRouter

router = APIRouter(prefix="/v1/parents", tags=["parents"])

@router.get("")
def list_parents():
    return {"parents": []}
