from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class OrderProduct(BaseModel):
    title: str
    thumbnail: str
    amount: float
    attributes: Dict[str, Any]


class OrderHost(BaseModel):
    username: str
    profile_pic: str
    verification: Optional[str] = None


class Order(BaseModel):
    id: str
    created_at: datetime
    delivered: bool
    ready: bool
    host: OrderHost
    products: List[OrderProduct]


class CheckoutItem(BaseModel):
    # Assuming cart item structure based on docs
    product_id: str
    quantity: int


class CheckoutDataRequest(BaseModel):
    data: List[CheckoutItem]
    location_index: Optional[float] = None


class CheckoutDataResponse(BaseModel):
    total: float
    distances: List[float]


class CheckoutConfirmRequest(BaseModel):
    data: List[CheckoutItem]
    phone: str
    location_index: Optional[float] = None


class CheckoutConfirmResponse(BaseModel):
    status: str
    order: str
    token: str


class PlaceOrderRequest(BaseModel):
    order_ref: str
    token: str
    cart: List[CheckoutItem]
    location_index: Optional[float] = None


class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
