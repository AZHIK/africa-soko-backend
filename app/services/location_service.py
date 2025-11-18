from typing import List, Optional
from sqlmodel import Session, select
from app.models.user import Address
from app.schemas.location import LocationCreate
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_user_locations(user_id: int, session: AsyncSession) -> List[Address]:
    """
    Retrieves all addresses for a given user.
    """
    result = await session.execute(select(Address).where(Address.user_id == user_id))
    addresses = result.scalars().all()
    return addresses


def normalize_location(data: dict) -> dict:
    # coordinates → latitude, longitude
    coords = data.get("coordinates")
    if coords and len(coords) == 2:
        data["latitude"] = coords[0]
        data["longitude"] = coords[1]

    # full_name MUST NEVER be null (DB constraint)
    if not data.get("full_name"):
        # Take the title from the frontend
        if data.get("title"):
            data["full_name"] = data["title"]
        else:
            data["full_name"] = "Unnamed Location"

    # address → street
    if not data.get("street") and data.get("address"):
        data["street"] = data["address"]

    # Remove frontend-only fields
    data.pop("coordinates", None)
    data.pop("title", None)
    data.pop("address", None)

    return data


async def add_user_location(user_id: int, location_data: LocationCreate, session):
    try:
        data = normalize_location(location_data.model_dump())

        db_address = Address(user_id=user_id, **data)

        session.add(db_address)
        await session.commit()
        await session.refresh(db_address)

        return db_address

    except Exception as e:
        print("🔥 ERROR WHEN INSERTING ADDRESS:", e)
        await session.rollback()
        raise e


def delete_user_location(
    user_id: int, location_id: int, session: Session
) -> Optional[Address]:
    """
    Deletes a specific address for a user.
    """
    address = session.exec(
        select(Address).where(Address.id == location_id, Address.user_id == user_id)
    ).first()
    if address:
        session.delete(address)
        session.commit()
        return address
    return None
