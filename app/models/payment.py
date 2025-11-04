from typing import Optional
from datetime import datetime
from enum import Enum
from .order import Order
from sqlmodel import SQLModel, Field, Relationship


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class PaymentMethod(str, Enum):
    credit_card = "credit_card"
    mobile_money = "mobile_money"
    cash_on_delivery = "cash_on_delivery"


class Payment(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    amount: float = Field(default=0.0)
    payment_method: PaymentMethod = Field(
        default=PaymentMethod.credit_card, sa_column_kwargs={"nullable": False}
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.pending, sa_column_kwargs={"nullable": False}
    )
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    order: Optional["Order"] = Relationship()
