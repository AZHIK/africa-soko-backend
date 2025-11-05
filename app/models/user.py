from typing import List, Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


class RolePermissionLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    permission_id: Optional[int] = Field(default=None, foreign_key="permission.id")
    created_at: datetime = Field(default_factory=datetime.now)


class UserRoleLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    assigned_at: datetime = Field(default_factory=datetime.now)


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # relationships
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permissions: List["Permission"] = Relationship(
        back_populates="roles", link_model=RolePermissionLink
    )


class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)  # human readable name
    code: str = Field(nullable=False, unique=True)  # machine code e.g. "product:create"
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # relationships
    roles: List[Role] = Relationship(
        back_populates="permissions", link_model=RolePermissionLink
    )


class UserPermissionOverride(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    permission_id: Optional[int] = Field(default=None, foreign_key="permission.id")
    is_granted: bool = Field(default=True)  # True = grant, False = revoke
    created_at: datetime = Field(default_factory=datetime.now)

    # relationships
    permission: Optional[Permission] = Relationship()


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True, index=True)
    username: Optional[str] = Field(default=None, index=True)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    is_vendor: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # relationships
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRoleLink)
    permission_overrides: List[UserPermissionOverride] = Relationship()


class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    full_name: str = Field(nullable=False)
    phone_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    user: Optional["User"] = Relationship()
