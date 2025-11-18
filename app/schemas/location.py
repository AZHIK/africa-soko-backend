from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class LocationBase(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False

    # Frontend fields
    title: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[list[float]] = None


# For creating a new location
class LocationCreate(LocationBase):
    pass


# Returned to frontend
class LocationRead(LocationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LocationWrapper(BaseModel):
    location: LocationCreate | LocationRead


# Response format
class MessageResponse(BaseModel):
    status: str
    message: Optional[str] = None


# New schema for capturing location coordinates with an optional dummy full_name
class LocationCaptureRequest(BaseModel):
    latitude: float
    longitude: float
    full_name: Optional[str] = "Captured Location"  # Default dummy value
