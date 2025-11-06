from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.user import User
from app.models.product import Review, Product
from app.models.vendor import Vendor, Store
from app.schemas.product_shema import ReviewCreate, ReviewRead, ReviewUpdate
from app.routers.auth import get_current_user

router = APIRouter(tags=["Reviews"])


async def get_vendor_stores(user_id: int, session: AsyncSession) -> List[int]:
    vendor_result = await session.execute(
        select(Vendor).where(Vendor.user_id == user_id)
    )
    vendor = vendor_result.scalars().first()
    if not vendor:
        return []

    stores_result = await session.execute(
        select(Store).where(Store.vendor_id == vendor.id)
    )
    return [store.id for store in stores_result.scalars().all()]


@router.post("/products/{product_id}/reviews", response_model=ReviewRead)
async def create_review(
    product_id: int,
    review_data: ReviewCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Check if product exists
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # A user can only review a product once
    existing_review = await session.execute(
        select(Review).where(
            Review.product_id == product_id, Review.user_id == current_user.id
        )
    )
    if existing_review.scalars().first():
        raise HTTPException(
            status_code=400, detail="You have already reviewed this product."
        )

    db_review = Review.model_validate(
        review_data, update={"user_id": current_user.id, "product_id": product_id}
    )
    session.add(db_review)
    await session.commit()
    await session.refresh(db_review)
    return db_review


@router.get("/products/{product_id}/reviews", response_model=List[ReviewRead])
async def get_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    reviews_result = await session.execute(
        select(Review).where(Review.product_id == product_id).offset(skip).limit(limit)
    )
    return reviews_result.scalars().all()


@router.put("/reviews/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_review = await session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found.")

    if db_review.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this review."
        )

    update_data = review_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)

    session.add(db_review)
    await session.commit()
    await session.refresh(db_review)
    return db_review


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_review = await session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # User can delete their own review.
    # A vendor can delete any review on their product.

    is_owner = db_review.user_id == current_user.id

    is_vendor_of_product = False
    if current_user.is_vendor:
        product = await session.get(Product, db_review.product_id)
        vendor_stores = await get_vendor_stores(
            current_user.id, session
        )  # I need this helper function
        if product and product.store_id in vendor_stores:
            is_vendor_of_product = True

    if not is_owner and not is_vendor_of_product:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this review."
        )

    await session.delete(db_review)
    await session.commit()
