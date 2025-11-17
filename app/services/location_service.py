from typing import List, Optional
from sqlmodel import Session, select
from app.models.user import Address
from app.schemas.location import LocationCreate


def get_user_locations(user_id: int, session: Session) -> List[Address]:
    """
    Retrieves all addresses for a given user.
    """
    addresses = session.exec(select(Address).where(Address.user_id == user_id)).all()
    return addresses


def add_user_location(
    user_id: int, location_data: LocationCreate, session: Session
) -> Address:
    """
    Creates a new address for a user.
    """
    db_address = Address(user_id=user_id, **location_data.model_dump())
    session.add(db_address)
    session.commit()
    session.refresh(db_address)
    return db_address


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
