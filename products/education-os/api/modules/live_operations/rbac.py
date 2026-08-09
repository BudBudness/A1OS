
from fastapi import APIRouter

router=APIRouter(prefix="/v1/rbac",tags=["rbac"])

roles=[
    "director",
    "head_mistress",
    "teacher",
    "staff",
    "parent"
]

@router.get("/roles")
def get_roles():

    return {
        "roles":roles
    }
