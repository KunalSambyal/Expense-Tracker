from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.db.session import get_db, AsyncSession
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.response import APIResponse
from app.core.dependencies import get_current_user
from app.services.category_service import CategoryService

category_router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@category_router.post("", response_model=APIResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
async def add_category(category_data: CategoryCreate, db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    existing_category = await CategoryService.get_by_name(db, category_data.name, current_user.id)

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category_data.name}' already exists."
        )

    new_category = await CategoryService.create(db, category_data, current_user.id)

    return APIResponse(
        code=201,
        message="Category created successfully",
        data=new_category
    )

@category_router.get("", response_model=APIResponse[list[CategoryResponse]], status_code=status.HTTP_200_OK)
async def get_categories(db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    categories = await CategoryService.get_all_by_user(db, current_user.id)

    return APIResponse(
        message="Categories retrieved successfully",
        data=categories
    )


@category_router.delete("/{category_id}", response_model=APIResponse[CategoryResponse], status_code=status.HTTP_200_OK)
async def delete_category(category_id: UUID, db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    category = await CategoryService.get_by_id(db, category_id, current_user.id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    await CategoryService.delete(db, category)
    
    return APIResponse(
        message="Category deleted successfully",
        data=category
    )