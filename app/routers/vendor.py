from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.vendor_schema import VendorCreate, VendorRead, VendorUpdate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorRead)
async def create_vendor_profile(
    vendor_data: VendorCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Check if user is already a vendor
    vendor_result = await session.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    if vendor_result.scalars().first():
        raise HTTPException(status_code=400, detail="User is already a vendor.")

    # Check if vendor_data.user_id matches current_user.id
    if vendor_data.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Cannot create a vendor profile for another user."
        )

    # Create vendor profile
    db_vendor = Vendor.model_validate(vendor_data)

    # Set user as vendor
    current_user.is_vendor = True
    session.add(current_user)

    session.add(db_vendor)
    await session.commit()
    await session.refresh(db_vendor)
    return db_vendor


@router.get("/", response_model=List[VendorRead])
async def list_vendors(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """
    Public endpoint to list all vendors.
    """
    query = select(Vendor).offset(skip).limit(limit)
    results = await session.execute(query)
    return results.scalars().all()


@router.get("/me", response_model=VendorRead)
async def get_my_vendor_profile(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="User is not a vendor.")

    vendor_result = await session.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = vendor_result.scalars().first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor profile not found.")
    return vendor


@router.get("/{vendor_id}", response_model=VendorRead)
async def get_vendor(
    vendor_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Public endpoint to get a single vendor by ID.
    """
    vendor = await session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put("/me", response_model=VendorRead)
async def update_my_vendor_profile(
    vendor_data: VendorUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="User is not a vendor.")

    vendor_result = await session.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    db_vendor = vendor_result.scalars().first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor profile not found.")

    update_data = vendor_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vendor, key, value)

    session.add(db_vendor)
    await session.commit()
    await session.refresh(db_vendor)
    return db_vendor
