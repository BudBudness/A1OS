from fastapi import APIRouter

router = APIRouter(
    prefix="/director/profile",
    tags=["Director Profile"]
)

@router.get("/")
@router.get("")
def get_profile():
    return {
        "status": "ok",
        "module": "Director School Profile Editor",
        "version": "1.1.0",
        "editable": True,
        "fields": [
            "school_name",
            "slogan",
            "address",
            "contact",
            "branding",
            "about"
        ]
    }

@router.post("/")
@router.post("")
def save_profile(payload: dict):
    return {
        "status": "saved",
        "editable": True,
        "profile": payload
    }
