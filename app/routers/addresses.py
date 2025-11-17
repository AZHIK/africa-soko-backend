from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.models.user import User, Address
from app.schemas.address_schema import AddressCreate, AddressUpdate, AddressResponse
from app.routers.auth import get_current_user
from typing import List

router = APIRouter(tags=["Addresses"])


@router.post(
    "/addresses/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED
)
async def create_address(
    address: AddressCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # If the new address is set as default, unset all other default addresses for the user
    if address.is_default:
        await db.execute(
            select(Address)
            .where(Address.user_id == current_user.id, Address.is_default)
            .update({"is_default": False})
        )

    db_address = Address(**address.dict(), user_id=current_user.id)
    db.add(db_address)
    await db.commit()
    await db.refresh(db_address)
    return db_address


@router.get("/addresses/", response_model=List[AddressResponse])
async def get_addresses(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Address).where(Address.user_id == current_user.id))
    addresses = result.scalars().all()
    return addresses


@router.get("/addresses/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Address).where(
            Address.id == address_id, Address.user_id == current_user.id
        )
    )
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address: AddressUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Address).where(
            Address.id == address_id, Address.user_id == current_user.id
        )
    )
    db_address = result.scalars().first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")

    update_data = address.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_address, key, value)

    # If the address is being set as default, unset all other default addresses for the user
    if "is_default" in update_data and update_data["is_default"]:
        await db.execute(
            select(Address)
            .where(
                Address.user_id == current_user.id,
                Address.is_default,
                Address.id != address_id,
            )
            .update({"is_default": False})
        )

    db.add(db_address)
    await db.commit()
    await db.refresh(db_address)
    return db_address


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Address).where(
            Address.id == address_id, Address.user_id == current_user.id
        )
    )
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    await db.delete(address)
    await db.commit()
    return {"ok": True}


@router.post("/addresses/{address_id}/set_default", response_model=AddressResponse)
async def set_default_address(
    address_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Unset all other default addresses for the user
    await db.execute(
        select(Address)
        .where(Address.user_id == current_user.id, Address.is_default)
        .update({"is_default": False})
    )

    # Set the specified address as default
    result = await db.execute(
        select(Address).where(
            Address.id == address_id, Address.user_id == current_user.id
        )
    )
    db_address = result.scalars().first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")

    db_address.is_default = True
    db.add(db_address)
    await db.commit()
    await db.refresh(db_address)
    return db_address
