from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.product import Product, Category
from app.models.user import User
from app.models.vendor import Vendor, Store
from app.schemas.product_shema import ProductCreate, ProductRead, ProductUpdate
from app.routers.auth import get_current_user
from pydantic import BaseModel
from sqlalchemy import or_

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


@router.get("/", response_model=List[ProductRead])
async def list_products(
    store_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    search: Optional[str] = Query(None, description="Search by name or description"),
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """
    Public endpoint: List active products with optional filters:
    store_id, category_id, min_price, max_price, search.
    """
    query = select(Product).where(Product.is_active)

    if store_id:
        query = query.where(Product.store_id == store_id)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(Product.name.ilike(search_term), Product.description.ilike(search_term))
        )

    results = await session.execute(query.offset(skip).limit(limit))
    return results.scalars().all()


# ----------------------
# Public: Get single product
# ----------------------
@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ----------------------
# Authenticated: Create product
# ----------------------
@router.post("/", response_model=ProductRead)
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

    db_product = Product.model_validate(product)
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    return db_product


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
