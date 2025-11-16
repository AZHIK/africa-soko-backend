from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.vendor_schema import VendorInfo


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


class ProductDisplay(BaseModel):
    id: int
    title: str
    price: float
    discount_price: Optional[float]
    stock: int
    unit_type: str
    description: Optional[str]
    category_id: Optional[int]
    host_id: Optional[int]
    images: List[str] = []
    host: VendorInfo
    created_at: datetime
    updated_at: datetime


class ProductFilter(BaseModel):
    store_id: Optional[int] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 20


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
