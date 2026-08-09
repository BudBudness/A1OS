
from fastapi import APIRouter
from api.a1os_core.intelligence.engine import system_insights

router = APIRouter(prefix="/v1/a1os", tags=["a1os-core"])

@router.get("/core/status")
def core_status():
    return {
        "platform":"A1OS Core",
        "version":"1.0",
        "source":"Little Oaks v4.8",
        "status":"operational"
    }

@router.get("/intelligence/status")
def intelligence_status():
    return system_insights()
