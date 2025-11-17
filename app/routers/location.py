from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.location import (
    LocationRead,
    LocationWrapper,
    MessageResponse,
)
from app.services import location_service
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter()


@router.post("/get_user_locations", response_model=List[LocationRead])
def get_user_locations_endpoint(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all locations for the authenticated user.
    """
    return location_service.get_user_locations(current_user.id, session)


@router.post("/add_user_location", response_model=MessageResponse)
def add_user_location_endpoint(
    req: LocationWrapper,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Add a new location for the authenticated user.
    """
    try:
        location_service.add_user_location(current_user.id, req.location, session)
        return MessageResponse(status="success", message="Location added successfully.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add location: {e}",
        )


@router.post("/delete_user_location", response_model=MessageResponse)
def delete_user_location_endpoint(
    req: LocationWrapper,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a location belonging to the authenticated user.
    """
    deleted_location = location_service.delete_user_location(
        current_user.id, req.location.id, session
    )

    if not deleted_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found or not owned by user.",
        )

    return MessageResponse(status="success", message="Location deleted successfully.")
