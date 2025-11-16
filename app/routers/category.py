from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.product import Category
from app.models.user import User
from app.schemas.category_schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="The user is not an administrator")
    return current_user


@router.post(
    "/", response_model=CategoryRead, dependencies=[Depends(get_current_admin_user)]
)
async def create_category(
    category: CategoryCreate, session: AsyncSession = Depends(get_session)
):
    # if category.parent_id:
    #     # parent_category = await session.get(Category, category.parent_id)  # noqa: F841
    #     # if not parent_category:
    #     #     raise HTTPException(
    #     #         status_code=400,
    #     #         detail=f"Parent category with id {category.parent_id} not found",
    #     #     )
    db_category = Category.model_validate(category)
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category


@router.get("/", response_model=List[CategoryRead])
async def list_categories(
    skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Category).offset(skip).limit(limit))
    categories = result.scalars().all()
    return categories


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: AsyncSession = Depends(get_session)):
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(get_current_admin_user)],
)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
):
    db_category = await session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.parent_id is not None:
        parent_category = await session.get(Category, category.parent_id)
        if not parent_category:
            raise HTTPException(
                status_code=400,
                detail=f"Parent category with id {category.parent_id} not found",
            )
    category_data = category.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category


@router.delete(
    "/{category_id}", status_code=204, dependencies=[Depends(get_current_admin_user)]
)
async def delete_category(
    category_id: int, session: AsyncSession = Depends(get_session)
):
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(category)
    await session.commit()
    return {"ok": True}
