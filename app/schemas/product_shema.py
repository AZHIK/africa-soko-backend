from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProductBase(BaseModel):
    store_id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str]
    price: float
    discount_price: Optional[float]
    stock: int
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str]
    slug: Optional[str]
    description: Optional[str]
    price: Optional[float]
    discount_price: Optional[float]
    stock: Optional[int]
    is_active: Optional[bool]


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime


# Schemas for Review
class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    product_id: int


class ReviewUpdate(ReviewBase):
    rating: Optional[int] = None


class ReviewRead(ReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime


# Schemas for ProductImage
class ImageBase(BaseModel):
    image_url: str
    is_main: bool = False


class ImageCreate(ImageBase):
    product_id: int


class ImageUpdate(ImageBase):
    image_url: Optional[str] = None
    is_main: Optional[bool] = None


class ImageRead(ImageBase):
    id: int
    product_id: int
