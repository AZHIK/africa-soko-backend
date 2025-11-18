from datetime import datetime
from typing import Annotated, Optional, List
from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    email: EmailStr
    username: str | None = None


class UserCreate(UserBase):
    is_admin: bool = False
    password: Annotated[str, constr(min_length=8, max_length=72)]
    role_name: str = "customer"


class UserRead(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role_name: Optional[str] = None
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleLogin(BaseModel):
    token: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Schemas from documentation


class ProfileLocation(BaseModel):
    address: str
    coordinates: List[float]


class UserProfileData(BaseModel):
    id: str
    username: str
    name: str
    full_name: str
    profile_pic: str
    verification: Optional[str] = None
    bio: str
    locations: List[ProfileLocation]
    categories: List[str]


class UserProfileResponse(BaseModel):
    status: str
    data: UserProfileData


class GetUserProfileRequest(BaseModel):
    id: str


class UpdateUserData(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    profile_pic: Optional[str] = None
    bio: Optional[str] = None


class UpdateUserRequest(BaseModel):
    id: str
    data: UpdateUserData


class UpdateUserResponse(BaseModel):
    status: str
    message: str


class UsernamesUser(BaseModel):
    id: str
    name: str
    full_name: str
    username: str
    profile_pic: str
    bio: Optional[str] = None


class GetUsernamesResponse(BaseModel):
    status: str
    user: UsernamesUser
    usernames: List[str]
    user_id: str


class GetUsernamesRequest(BaseModel):
    id: str


class FollowUserRequest(BaseModel):
    user_id: str
    target_id: str


class FollowUserResponse(BaseModel):
    follow_state: str  # "followed" or "unfollowed"


class UserLocation(BaseModel):
    title: str
    address: str
    coordinates: List[float]


class GetUserLocationsRequest(BaseModel):
    id: str


class AddUserLocationRequest(BaseModel):
    id: str
    location: UserLocation


class DeleteUserLocationRequest(BaseModel):
    id: str
    location: UserLocation


class StatusResponse(BaseModel):
    status: str
