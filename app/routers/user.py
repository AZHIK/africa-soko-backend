from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import os
from uuid import uuid4

from app.models.user import User
from app.db.session import get_session
from app.routers.auth import get_current_user
from app.core.config import settings

router = APIRouter(tags=["user"])


@router.post("/update_user")
async def update_user(
    data: dict,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Expects JSON:
    {
        "data": { "username": "...", "email": "...", "profile_pic": "..." }
    }
    """
    changes = data.get("data")
    if not changes:
        return JSONResponse(
            {"status": "failed", "detail": "Missing data"}, status_code=400
        )

    # Update allowed fields only
    allowed_fields = {"username", "email", "profile_pic"}  # extend as needed
    for key, value in changes.items():
        if key in allowed_fields:
            setattr(current_user, key, value)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return {
        "status": "success",
        "message": "Profile updated",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "profile_pic": current_user.profile_pic,
        },
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles file uploads. Returns filename for frontend.
    """
    upload_dir = os.path.join(settings.BASE_DIR, "sokoni_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    ext = file.filename.split(".")[-1]
    filename = f"profile_{uuid4().hex}.{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"status": "success", "filename": filename}
