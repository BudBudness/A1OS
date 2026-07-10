from fastapi import File, UploadFile, HTTPException
import os
import shutil
from datetime import datetime

UPLOAD_DIR = "uploads"

async def upload_file(file: UploadFile) -> dict:
    if not file:
        raise HTTPException(400, "No file provided")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": filename,
        "path": filepath,
        "size": os.path.getsize(filepath),
        "uploaded": datetime.now().isoformat()
    }
