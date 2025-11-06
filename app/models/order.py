from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from .user import User
from .vendor import Store

if TYPE_CHECKING:
    from .payment import Payment
    from .delivery import Delivery  # new model to be created
    from .product import Product


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    store_id: int = Field(foreign_key="store.id")

    status: OrderStatus = Field(
        default=OrderStatus.pending, sa_column_kwargs={"nullable": False}
    )
    total_amount: float = Field(default=0.0)
    shipping_cost: float = Field(default=0.0)
    discount: float = Field(default=0.0)
    tax: float = Field(default=0.0)
    grand_total: float = Field(default=0.0)

    shipping_method: Optional[str] = Field(default="standard")
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    shipping_address_id: int = Field(foreign_key="address.id")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    items: List["OrderItem"] = Relationship(back_populates="order")
    user: Optional["User"] = Relationship()
    store: Optional["Store"] = Relationship()
    payment: Optional["Payment"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"uselist": False}
    )
    delivery: Optional["Delivery"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"uselist": False}
    )


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1)
    unit_price: float = Field(default=0.0)
    subtotal: float = Field(default=0.0)

    order: Optional["Order"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship()  # type: ignore # noqa: F821
