from typing import Optional
from datetime import datetime
from .product import Product
from .user import User
from sqlmodel import SQLModel, Field, Relationship


class WishlistItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    added_at: datetime = Field(default_factory=datetime.now)

    product: Optional["Product"] = Relationship()
    user: Optional["User"] = Relationship()


class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1)
    added_at: datetime = Field(default_factory=datetime.now)

    product: Optional["Product"] = Relationship()
    user: Optional["User"] = Relationship()
