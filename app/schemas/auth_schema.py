from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, constr
from typing import Annotated, Optional


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., alias="___refresh_token")


class RefreshTokenResponse(BaseModel):
    access_token: str = Field(..., alias="___access_token")
    refresh_token: Optional[str] = Field(None, alias="___refresh_token")


class EmailLoginRequest(BaseModel):
    email: str = Field(..., alias="___email")
    password: str = Field(..., alias="___password")


class LoginResponse(BaseModel):
    access_token: str = Field(..., alias="___access_token")
    refresh_token: str = Field(..., alias="___refresh_token")
    role: Optional[str] = None
    is_new: bool = False


class UserBase(BaseModel):
    email: EmailStr
    username: str | None = None


class UserCreate(UserBase):
    is_admin: bool = False
    password: Annotated[str, constr(min_length=8, max_length=72)]


class UserRead(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
