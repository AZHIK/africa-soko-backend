from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from .user import User
from .vendor import Store
from sqlmodel import SQLModel, Field, Relationship
# from .product import Product

if TYPE_CHECKING:
    from .payment import Payment


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    store_id: Optional[int] = Field(default=None, foreign_key="store.id")
    status: OrderStatus = Field(
        default=OrderStatus.pending, sa_column_kwargs={"nullable": False}
    )
    total_amount: float = Field(default=0.0)
    shipping_address_id: Optional[int] = Field(default=None, foreign_key="address.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    items: List["OrderItem"] = Relationship(back_populates="order")
    user: Optional["User"] = Relationship()
    store: Optional["Store"] = Relationship()
    payment: Optional["Payment"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"uselist": False}
    )


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    quantity: int = Field(default=1)
    unit_price: float = Field(default=0.0)
    subtotal: float = Field(default=0.0)

    order: Optional["Order"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship()  # type: ignore # noqa: F821
