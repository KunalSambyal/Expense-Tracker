from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.db.session import get_db, AsyncSession
from app.models.user import User
from app.models.expense import Expense
from app.models.category import Category
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.schemas.response import APIResponse
from app.core.dependencies import get_current_user

expenses_router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])


@expenses_router.post(
    "", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_201_CREATED
)
async def add_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user),
):
    category_query = select(Category).where(
        Category.id == expense_data.category_id, Category.user_id == current_user.id
    )
    category = (await db.execute(category_query)).scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or does not belong to user.",
        )

    new_expense = Expense(**expense_data.model_dump(), user_id=current_user.id)

    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)

    return APIResponse(
        code=201,
        message="Expense created successfully", 
        data=new_expense
    )
