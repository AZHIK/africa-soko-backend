from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.user import User
from app.models.vendor import Vendor, Store
from app.schemas.vendor_schema import StoreCreate, StoreRead, StoreUpdate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/stores", tags=["Stores"])


# Helper to get vendor
async def get_vendor_from_user(user_id: int, session: AsyncSession) -> Vendor:
    vendor_result = await session.execute(
        select(Vendor).where(Vendor.user_id == user_id)
    )
    vendor = vendor_result.scalars().first()
    if not vendor:
        raise HTTPException(status_code=403, detail="User is not a vendor.")
    return vendor


@router.post("/", response_model=StoreRead)
async def create_store(
    store_data: StoreCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vendor = await get_vendor_from_user(current_user.id, session)

    if store_data.vendor_id != vendor.id:
        raise HTTPException(
            status_code=403, detail="Cannot create a store for another vendor."
        )

    db_store = Store.model_validate(store_data)
    session.add(db_store)
    await session.commit()
    await session.refresh(db_store)
    return db_store


@router.get("/", response_model=List[StoreRead])
async def list_stores(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """
    Public endpoint to list all stores.
    """
    query = select(Store).offset(skip).limit(limit)
    results = await session.execute(query)
    return results.scalars().all()


@router.get("/me", response_model=List[StoreRead])
async def get_my_stores(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vendor = await get_vendor_from_user(current_user.id, session)

    stores_result = await session.execute(
        select(Store).where(Store.vendor_id == vendor.id)
    )
    return stores_result.scalars().all()


@router.get("/{store_id}", response_model=StoreRead)
async def get_store(
    store_id: int,
    session: AsyncSession = Depends(get_session),
):
    # Public endpoint to view a store
    store = await session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")
    return store


@router.put("/{store_id}", response_model=StoreRead)
async def update_store(
    store_id: int,
    store_data: StoreUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    vendor = await get_vendor_from_user(current_user.id, session)

    db_store = await session.get(Store, store_id)
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found.")

    if db_store.vendor_id != vendor.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this store."
        )

    update_data = store_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_store, key, value)

    session.add(db_store)
    await session.commit()
    await session.refresh(db_store)
    return db_store
