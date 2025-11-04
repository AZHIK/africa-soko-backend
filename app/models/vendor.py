from typing import List, Optional
from datetime import datetime
from .user import User
from .product import Product
from sqlmodel import SQLModel, Field, Relationship


class Vendor(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", unique=True)
    business_name: str = Field(nullable=False)
    business_email: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # relationships
    user: Optional["User"] = Relationship()
    stores: List["Store"] = Relationship(back_populates="vendor")


class Store(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    vendor_id: Optional[int] = Field(default=None, foreign_key="vendor.id")
    store_name: str = Field(nullable=False)
    slug: str = Field(nullable=False, index=True, unique=True)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: bool = Field(default=False)
    rating: Optional[float] = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    vendor: Optional[Vendor] = Relationship(back_populates="stores")
    products: List["Product"] = Relationship(back_populates="store")
