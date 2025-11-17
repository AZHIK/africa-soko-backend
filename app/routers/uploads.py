from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
from uuid import uuid4

router = APIRouter()

UPLOAD_DIR = "sokoni_uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload", tags=["File Upload"])
async def upload_file(file: UploadFile = File(...)):
    """
    A general-purpose endpoint for uploading files (profile pictures, story media, etc.).
    """
    try:
        # Generate a unique filename
        filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return JSONResponse(status_code=200, content={"filename": filename})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
