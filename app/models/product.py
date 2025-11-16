from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from .user import User


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: int = Field(foreign_key="store.id")
    category_id: int = Field(foreign_key="category.id")
    name: str = Field(nullable=False, index=True)
    slug: str = Field(nullable=False, index=True, unique=True)
    description: Optional[str] = None
    price: float = Field(nullable=False)
    discount_price: Optional[float] = None
    stock: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    store: Optional["Store"] = Relationship(  # noqa: F821 # pyright: ignore[reportUndefinedVariable]
        back_populates="products", sa_relationship_kwargs={"lazy": "joined"}
    )  # type: ignore # noqa: F821
    category: Optional["Category"] = Relationship(
        back_populates="products", sa_relationship_kwargs={"lazy": "joined"}
    )
    images: List["ProductImage"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True, index=True)
    slug: str = Field(nullable=False, unique=True, index=True)
    description: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    children: List["Category"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Category.id", "lazy": "selectin"}
    )
    products: List["Product"] = Relationship(
        back_populates="category", sa_relationship_kwargs={"lazy": "selectin"}
    )


class ProductImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    image_url: str = Field(nullable=False)
    is_main: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    product: Optional["Product"] = Relationship(back_populates="images")


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    rating: int = Field(default=5, ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship()
    product: Optional["Product"] = Relationship(back_populates="reviews")
