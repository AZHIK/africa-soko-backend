from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.order_schema import (
    GetOrdersRequest,
    Order,
    MarkOrderReadyRequest,
    CheckoutDataRequest,
    CheckoutDataResponse,
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    PlaceOrderRequest,
    StatusResponse,
)
from typing import List

router = APIRouter(tags=["Orders"])


@router.post("/get_orders", response_model=List[Order])
async def get_orders(
    request: GetOrdersRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return []


@router.post("/get_client_orders", response_model=List[Order])
async def get_client_orders(
    request: GetOrdersRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return []


@router.post("/mark_order_ready", response_model=StatusResponse)
async def mark_order_ready(
    request: MarkOrderReadyRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return {"status": "success"}


@router.post("/checkout_data", response_model=CheckoutDataResponse)
async def checkout_data(
    request: CheckoutDataRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return {"total": 0.0, "distances": []}


@router.post("/checkout_confirm", response_model=CheckoutConfirmResponse)
async def checkout_confirm(
    request: CheckoutConfirmRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return {"status": "success", "order": "some_order_id", "token": "some_token"}


@router.post("/place_order", response_model=StatusResponse)
async def place_order(
    request: PlaceOrderRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return {"status": "success", "message": "Order placed successfully"}
