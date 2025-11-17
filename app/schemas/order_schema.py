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


class Order(BaseModel):
    id: str
    created_at: datetime
    delivered: bool
    ready: bool
    host: OrderHost
    products: List[OrderProduct]


class GetOrdersRequest(BaseModel):
    id: str


class MarkOrderReadyRequest(BaseModel):
    id: str


class CheckoutItem(BaseModel):
    # Assuming cart item structure based on docs
    product_id: str
    quantity: int


class CheckoutDataRequest(BaseModel):
    id: str
    data: List[CheckoutItem]
    location_index: int


class CheckoutDataResponse(BaseModel):
    total: float
    distances: List[float]


class CheckoutConfirmRequest(BaseModel):
    id: str
    data: List[CheckoutItem]
    phone: str
    location_index: int


class CheckoutConfirmResponse(BaseModel):
    status: str
    order: str
    token: str


class PlaceOrderRequest(BaseModel):
    id: str
    order_ref: str
    token: str
    cart: List[CheckoutItem]
    location_index: int


class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
