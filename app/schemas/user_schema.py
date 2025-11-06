from datetime import datetime
from typing import Annotated, Optional
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
