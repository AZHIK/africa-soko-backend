from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_session
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User, Address
from app.models.vendor import Store, Vendor
from app.schemas.order_schema import (
    Order as OrderSchema,
    OrderHost,
    OrderProduct,
    CheckoutDataRequest,
    CheckoutDataResponse,
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    PlaceOrderRequest,
    StatusResponse,
)
from typing import List
import uuid
import logging

from app.routers.auth import get_current_user

logger = logging.getLogger("checkout_logger")
logging.basicConfig(level=logging.INFO)


router = APIRouter(tags=["Orders"])


# ─── Get all orders for a user ────────────────────────────────────────────────
@router.post("/get_orders", response_model=List[OrderSchema])
async def get_orders(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.store)
            .selectinload(Store.vendor)
            .selectinload(Vendor.user),
        )
    )
    orders = result.scalars().unique().all()

    order_list = []
    for o in orders:
        if not o.store or not o.store.vendor or not o.store.vendor.user:
            # Skip orders with incomplete host data to prevent errors
            continue

        host = OrderHost(
            username=o.store.vendor.user.username or "unknown",
            profile_pic=o.store.vendor.user.profile_pic,
            verification="gold" if o.store.is_verified else "bronze",
        )
        products = []
        for item in o.items:
            if item.product:
                products.append(
                    OrderProduct(
                        title=item.product.name,
                        thumbnail=(
                            next(
                                (
                                    img.image_url
                                    for img in item.product.images
                                    if img.is_main
                                ),
                                None,
                            )
                            or (
                                item.product.images[0].image_url
                                if item.product.images
                                else ""
                            )
                        ),
                        amount=item.quantity,
                        attributes={},  # Frontend handles attributes display
                    )
                )
        order_list.append(
            OrderSchema(
                id=str(o.id),
                created_at=o.created_at,
                delivered=o.status == "delivered",
                ready=o.status in ["paid", "processing", "shipped"],
                host=host,
                products=products,
            )
        )
    return order_list


@router.post("/checkout_data", response_model=CheckoutDataResponse)
async def checkout_data(
    request: CheckoutDataRequest,
    db: AsyncSession = Depends(get_session),
):
    # Log the received data
    logger.info("Received checkout request: %s", request.json())

    cart = request.data
    if not cart:
        logger.info("Cart is empty")
        return CheckoutDataResponse(total=0.0, distances=[])

    total = 0.0
    for item in cart:
        logger.info("Processing item: %s", item)
        result = await db.execute(
            select(Product).where(Product.id == int(item.product_id))
        )
        product = result.scalars().first()
        if not product:
            logger.warning("Product %s not found", item.product_id)
            raise HTTPException(
                status_code=404, detail=f"Product {item.product_id} not found"
            )
        total += product.price * item.quantity

    distances = [0.0, 1.0, 2.0]
    logger.info("Returning total: %s, distances: %s", total, distances)

    return CheckoutDataResponse(total=total, distances=distances)


# ─── Checkout Confirm ────────────────────────────────────────────────────────
@router.post("/checkout_confirm", response_model=CheckoutConfirmResponse)
async def checkout_confirm(
    request: CheckoutConfirmRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order_ref = str(uuid.uuid4())
    token = str(uuid.uuid4())

    return CheckoutConfirmResponse(status="success", order=order_ref, token=token)


# ─── Place Order ─────────────────────────────────────────────────────────────
@router.post("/place_order", response_model=StatusResponse)
async def place_order(
    request: PlaceOrderRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Fetch user
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not request.cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Fetch the user's default shipping address
    default_address_result = await db.execute(
        select(Address).where(Address.user_id == user.id, Address.is_default)
    )
    default_address = default_address_result.scalars().first()

    # if not default_address:
    #     raise HTTPException(
    #         status_code=400, detail="No default shipping address found for the user."
    #     )

    shipping_address_id = default_address.id if default_address else None

    # Group items by store
    store_products = {}
    for item in request.cart:
        result = await db.execute(
            select(Product).where(Product.id == int(item.product_id))
        )
        product = result.scalars().first()
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {item.product_id} not found"
            )
        if product.store_id not in store_products:
            store_products[product.store_id] = []
        store_products[product.store_id].append((product, item.quantity))

    # Create one order per store
    for store_id, products_in_store in store_products.items():
        total_amount = sum(p.price * q for p, q in products_in_store)

        # Create the order
        order = Order(
            user_id=user.id,
            store_id=store_id,
            status="paid",
            total_amount=total_amount,
            grand_total=total_amount,
            shipping_address_id=shipping_address_id,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)

        # Add order items
        for product, quantity in products_in_store:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
                subtotal=product.price * quantity,
            )
            db.add(order_item)
        await db.commit()

    return StatusResponse(status="success", message="Order(s) placed successfully")
