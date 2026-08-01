from fastapi import APIRouter

router = APIRouter(prefix="/v1/classrooms", tags=["classrooms"])

@router.get("")
def list_classrooms():
    return {"classrooms": []}
