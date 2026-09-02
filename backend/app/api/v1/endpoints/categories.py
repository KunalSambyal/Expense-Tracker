from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_

from app.db.session import get_db, AsyncSession
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.response import APIResponse
from app.core.dependencies import get_current_user

category_router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@category_router.post("", response_model=APIResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
async def add_category(category_data: CategoryCreate, db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    query = select(Category).where(Category.name == category_data.name, Category.user_id == current_user.id)
    existing_category = (await db.execute(query)).scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category_data.name}' already exists."
        )

    new_category = Category(
        name=category_data.name,
        user_id=current_user.id
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return APIResponse(
        code=201,
        message="Category created successfully",
        data=new_category
    )

@category_router.get("", response_model=APIResponse[list[CategoryResponse]], status_code=status.HTTP_200_OK)
async def get_categories(db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    query = select(Category).where(Category.user_id == current_user.id)
    categories = (await db.execute(query)).scalars().all()

    return APIResponse(
        message="Categories retrieved successfully",
        data=categories
    )


@category_router.delete("/{category_id}", response_model=APIResponse[CategoryResponse], status_code=status.HTTP_200_OK)
async def delete_category(category_id, db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    query = select(Category).where(and_(
        Category.user_id == current_user.id,
        Category.id == category_id
    ))
    category = (await db.execute(query)).scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    await db.delete(category)
    await db.commit()
    
    return APIResponse(
        message="Category deleted successfullfy",
        data=category
    )