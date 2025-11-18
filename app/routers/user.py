from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import os
from uuid import uuid4
from sqlmodel import select


from app.models.user import User
from app.db.session import get_session
from app.routers.auth import get_current_user
from app.core.config import settings
from app.schemas.user_schema import (
    GetUsernamesRequest,
    GetUsernamesResponse,
    UsernamesUser,
)
from app.services.users_service import get_all_usernames
from app.core.jwt import decode_access_token

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


@router.post("/get_usernames", response_model=GetUsernamesResponse)
async def get_usernames(
    data: GetUsernamesRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Decodes a token to get user profile data and a list of all usernames.
    """
    token = data.id
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await session.execute(select(User).where(User.id == user_id))
    current_user = result.scalars().first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    usernames = await get_all_usernames(session)

    if current_user.first_name and current_user.last_name:
        name = f"{current_user.first_name} {current_user.last_name}"
    else:
        name = current_user.username

    user_data = UsernamesUser(
        id=str(current_user.id),
        name=name,
        full_name=name,
        username=current_user.username,
        profile_pic=current_user.profile_pic or "",
        bio=current_user.biography or "",
    )

    return GetUsernamesResponse(
        status="success",
        user=user_data,
        usernames=usernames,
        user_id=str(current_user.id),
    )
