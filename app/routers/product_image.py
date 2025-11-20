import os
import shutil
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.user import User
from app.models.product import Product, ProductImage
from app.models.vendor import Vendor, Store
from app.routers.uploads import UPLOAD_DIR
from app.schemas.product_shema import ImageRead
from app.routers.auth import get_current_user

router = APIRouter(tags=["Product Images"])


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


@router.post("/products/{product_id}/images", response_model=list[ImageRead])
async def add_product_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="Only vendors can add images.")

    vendor_stores = await get_vendor_stores(current_user.id, session)
    if product.store_id not in vendor_stores:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add images to this product.",
        )

    saved_images = []

    # Process multiple upload files
    for file in files:
        filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        db_image = ProductImage(product_id=product_id, image_url=filename)
        session.add(db_image)
        saved_images.append(db_image)

    await session.commit()

    # refresh all image instances
    for img in saved_images:
        await session.refresh(img)

    return saved_images


@router.get("/products/{product_id}/images", response_model=List[ImageRead])
async def get_product_images(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    images_result = await session.execute(
        select(ProductImage).where(ProductImage.product_id == product_id)
    )
    return images_result.scalars().all()


@router.delete("/images/{image_id}", status_code=204)
async def delete_product_image(
    image_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_image = await session.get(ProductImage, image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found.")

    product = await session.get(Product, db_image.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="Only vendors can delete images.")

    vendor_stores = await get_vendor_stores(current_user.id, session)
    if product.store_id not in vendor_stores:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this image."
        )

    await session.delete(db_image)
    await session.commit()


@router.post("/images/{image_id}/set-main", response_model=ImageRead)
async def set_main_image(
    image_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_image = await session.get(ProductImage, image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found.")

    product = await session.get(Product, db_image.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="Only vendors can set main image.")

    vendor_stores = await get_vendor_stores(current_user.id, session)
    if product.store_id not in vendor_stores:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this product's images."
        )

    other_images_result = await session.execute(
        select(ProductImage).where(ProductImage.product_id == product.id)
    )
    for img in other_images_result.scalars().all():
        img.is_main = False
        session.add(img)

    db_image.is_main = True
    session.add(db_image)
    await session.commit()
    await session.refresh(db_image)
    return db_image
