from fastapi import APIRouter, Depends
from pathlib import Path
import json

router = APIRouter(prefix="/director/profile", tags=["director"])

PROFILE = Path("director_profile.json")


@router.get("")
def get_profile():
    if PROFILE.exists():
        return json.loads(PROFILE.read_text())

    return {
        "school_name": "Little Oaks Montessori Nursery & Kindergarten",
        "slogan": "Nurture. Explore. Grow.",
        "location": "Insigiro Road",
        "description": "",
        "phone": "",
        "email": ""
    }


@router.put("")
def update_profile(data: dict):
    PROFILE.write_text(json.dumps(data, indent=2))
    return {
        "status": "updated",
        "profile": data
    }
