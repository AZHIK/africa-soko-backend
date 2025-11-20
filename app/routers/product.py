from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.product import Product, Category
from app.models.product import Review
from app.models.user import User
from app.models.vendor import Vendor, Store
from app.schemas.product_shema import (
    ProductCreate,
    ProductDisplay,
    ProductFilter,
    ProductRead,
    ProductUpdate,
)
from app.routers.auth import get_current_user
from pydantic import BaseModel
from sqlalchemy import or_, func

from app.schemas.vendor_schema import VendorInfo

router = APIRouter(prefix="/products", tags=["Products"])


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


# ----------------------
# Public: List Products
# ----------------------


@router.post("/get_products", response_model=List[ProductDisplay])
async def get_products(
    filters: ProductFilter,
    session: AsyncSession = Depends(get_session),
):
    avg_rating_subquery = (
        select(
            Review.product_id,
            func.avg(Review.rating).label("average_rating"),
        )
        .group_by(Review.product_id)
        .subquery()
    )

    query = (
        select(Product, avg_rating_subquery.c.average_rating)
        .outerjoin(avg_rating_subquery, Product.id == avg_rating_subquery.c.product_id)
        .where(Product.is_active)
    )

    if filters.store_id:
        query = query.where(Product.store_id == filters.store_id)
    if filters.category_id:
        query = query.where(Product.category_id == filters.category_id)
    if filters.min_price is not None:
        query = query.where(Product.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Product.price <= filters.max_price)
    if filters.search:
        search_term = f"%{filters.search.lower()}%"
        query = query.where(
            or_(Product.name.ilike(search_term), Product.description.ilike(search_term))
        )

    results = await session.execute(query.offset(filters.skip).limit(filters.limit))
    products_with_ratings = results.all()

    response = []
    for product, average_rating in products_with_ratings:
        vendor_user = (
            product.store.vendor.user
            if product.store and product.store.vendor
            else None
        )
        host_info = VendorInfo(
            id=product.store.vendor.id
            if product.store and product.store.vendor
            else None,
            username=vendor_user.username if vendor_user else "anonymous",
            profile_pic=vendor_user.profile_pic
            if vendor_user
            else "assets/images/faces/user1.jfif",
            verification="verified"
            if product.store and product.store.is_verified
            else "null",
            address=product.store.store_name if product.store else "N/A",
        )

        product_images = (
            [img.image_url for img in product.images] if product.images else []
        )

        response.append(
            ProductDisplay(
                id=product.id,
                title=product.name,
                price=product.price,
                discount_price=product.discount_price,
                stock=product.stock,
                unit_type="Item",
                description=product.description,
                category_id=product.category_id,
                host_id=product.store.vendor.id
                if product.store and product.store.vendor
                else None,
                images=product_images,
                host=host_info,
                created_at=product.created_at,
                updated_at=product.updated_at,
                average_rating=float(average_rating)
                if average_rating is not None
                else 0.0,
            )
        )
    return response


# ----------------------
# Public: Get single product
# ----------------------
@router.get("/{product_id}", response_model=ProductDisplay)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")

    reviews_result = await session.execute(
        select(Review).where(Review.product_id == product_id)
    )
    reviews = reviews_result.scalars().all()
    average_rating = 0.0
    if reviews:
        average_rating = sum(r.rating for r in reviews) / len(reviews)

    vendor_user = (
        product.store.vendor.user if product.store and product.store.vendor else None
    )
    host_info = VendorInfo(
        id=product.store.vendor.id if product.store and product.store.vendor else None,
        username=vendor_user.username if vendor_user else "anonymous",
        profile_pic=vendor_user.profile_pic
        if vendor_user
        else "assets/images/faces/user1.jfif",
        verification="verified"
        if product.store and product.store.is_verified
        else "null",
        address=product.store.store_name if product.store else "N/A",
    )

    product_images = [img.image_url for img in product.images] if product.images else []

    return ProductDisplay(
        id=product.id,
        title=product.name,
        price=product.price,
        discount_price=product.discount_price,
        stock=product.stock,
        unit_type="Item",
        description=product.description,
        category_id=product.category_id,
        host_id=product.store.vendor.id
        if product.store and product.store.vendor
        else None,
        images=product_images,
        host=host_info,
        created_at=product.created_at,
        updated_at=product.updated_at,
        average_rating=average_rating,
    )


# ----------------------
# Authenticated: Create product (with images & display-ready response)
# ----------------------
@router.post("/", response_model=ProductDisplay)
async def create_product(
    product: ProductCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="Only vendors can add products.")

    vendor_stores = await get_vendor_stores(current_user.id, session)
    if not vendor_stores:
        raise HTTPException(
            status_code=403, detail="Not authorized to add products without a store."
        )

    if product.store_id not in vendor_stores:
        raise HTTPException(
            status_code=403, detail="Cannot add product to a different store."
        )

    if product.category_id:
        category = await session.get(Category, product.category_id)
        if not category:
            raise HTTPException(
                status_code=400,
                detail=f"Category with id {product.category_id} not found",
            )

    # Create Product
    db_product = Product.model_validate(product)
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)

    # Prepare display response for frontend
    vendor_user = (
        db_product.store.vendor.user
        if db_product.store and db_product.store.vendor
        else None
    )
    host_info = VendorInfo(
        id=db_product.store.vendor.id
        if db_product.store and db_product.store.vendor
        else None,
        username=vendor_user.username if vendor_user else "anonymous",
        profile_pic=vendor_user.profile_pic
        if vendor_user
        else "assets/images/faces/user1.jfif",
        verification="verified"
        if db_product.store and db_product.store.is_verified
        else "null",
        address=db_product.store.store_name if db_product.store else "N/A",
    )

    product_images = (
        [img.image_url for img in db_product.images] if db_product.images else []
    )

    response = ProductDisplay(
        id=db_product.id,
        title=db_product.name,
        price=db_product.price,
        discount_price=db_product.discount_price,
        stock=db_product.stock,
        unit_type="Item",
        description=db_product.description,
        category_id=db_product.category_id,
        host_id=db_product.store.vendor.id
        if db_product.store and db_product.store.vendor
        else None,
        images=product_images,
        host=host_info,
        created_at=db_product.created_at,
        updated_at=db_product.updated_at,
        average_rating=0.0,
    )

    return response


# ----------------------
# Authenticated: Update product
# ----------------------
@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_product = await session.get(Product, product_id)
    if not db_product or not db_product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")

    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="Only vendors can update products.")

    vendor_stores = await get_vendor_stores(current_user.id, session)
    if db_product.store_id not in vendor_stores:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this product."
        )

    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    return db_product


# ----------------------
# Authenticated: Soft delete product
# ----------------------
class DeleteResponse(BaseModel):
    detail: str


@router.delete("/{product_id}", response_model=DeleteResponse)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_product = await session.get(Product, product_id)
    if not db_product or not db_product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")

    if not current_user.is_vendor:
        raise HTTPException(status_code=403, detail="Only vendors can delete products.")

    vendor_stores = await get_vendor_stores(current_user.id, session)
    if db_product.store_id not in vendor_stores:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this product."
        )

    db_product.is_active = False
    session.add(db_product)
    await session.commit()
    return DeleteResponse(detail=f"Product {product_id} deactivated successfully")
