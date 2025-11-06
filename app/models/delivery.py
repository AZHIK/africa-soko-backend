from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from .order import *  # noqa: F403


class DeliveryStatus(str, Enum):
    pending = "pending"
    dispatched = "dispatched"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"


class Delivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")

    courier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    delivery_status: DeliveryStatus = Field(default=DeliveryStatus.pending)
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    delivery_note: Optional[str] = None

    order: Optional["Order"] = Relationship(back_populates="delivery")  # noqa: F405
