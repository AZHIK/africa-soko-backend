from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


# Vendor Schemas
class VendorBase(BaseModel):
    business_name: str
    business_email: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None


class VendorCreate(VendorBase):
    user_id: int


class VendorUpdate(VendorBase):
    pass


class VendorRead(VendorBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class VendorInfo(BaseModel):
    id: Optional[int]
    username: str
    profile_pic: Optional[str] = None
    verification: Optional[str] = None
    address: Optional[str] = None


# Store Schemas
class StoreBase(BaseModel):
    store_name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class StoreCreate(StoreBase):
    vendor_id: int


class StoreUpdate(StoreBase):
    store_name: Optional[str] = None
    slug: Optional[str] = None


class StoreRead(StoreBase):
    id: int
    vendor_id: int
    is_verified: bool
    rating: Optional[float]
    created_at: datetime
    updated_at: datetime


class VendorReadWithStores(VendorRead):
    stores: List[StoreRead] = []


class StoreReadWithVendor(StoreRead):
    vendor: VendorRead
