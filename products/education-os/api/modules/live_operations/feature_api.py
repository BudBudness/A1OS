
from fastapi import APIRouter
router=APIRouter(prefix="/v1/features",tags=["features"])

@router.get("/flags")
def flags():
    return {
        "finance":True,
        "rbac":True,
        "parent_portal":True,
        "inventory":True,
        "notifications":True
    }
