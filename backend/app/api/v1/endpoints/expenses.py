from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
import uuid

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


@expenses_router.get("", response_model=APIResponse[list[ExpenseResponse]], status_code=status.HTTP_200_OK)
async def get_expenses(current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    query = select(Expense).where(Expense.user_id == current_user.id)
    user_expenses = (await db.execute(query)).scalars().all()

    return APIResponse(
        message="Expenses retrieved successfully.",
        data=user_expenses
    )


@expenses_router.get("/{expense_id}", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_200_OK)
async def get_expense(expense_id: uuid.UUID, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    query = select(Expense).where(and_(
        Expense.user_id == current_user.id,
        Expense.id == expense_id
    ))
    user_expense = (await db.execute(query)).scalar_one_or_none()

    if not user_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id: {expense_id} not found"
        )

    return APIResponse(
        message="Expense retrieved successfully.",
        data=user_expense
    )


@expenses_router.patch("/{expense_id}", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_200_OK)
async def update_expense(expense_id: uuid.UUID, expense_data: ExpenseUpdate, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    query = select(Expense).where(and_(
        Expense.user_id == current_user.id,
        Expense.id == expense_id
    ))
    existing_expense = (await db.execute(query)).scalar_one_or_none()

    if existing_expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id: {expense_id} not found"
        )

    update_data = expense_data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category_query = select(Category).where(Category.id == update_data["category_id"], Category.user_id == current_user.id)
        category_result = (await db.execute(category_query)).scalar_one_or_none()
        if not category_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or does not belong to the user"
            )


    for field, value in update_data.items():
        setattr(existing_expense, field, value)

    await db.commit()
    await db.refresh(existing_expense)

    return APIResponse(
        message="Expens updated successfully.",
        data=existing_expense
    )


@expenses_router.delete("/{expense_id}", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_200_OK)
async def delete_expense(expense_id: uuid.UUID, db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    query = select(Expense).where(and_(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ))
    expense = (await db.execute(query)).scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id: {expense_id} not found"
        )

    await db.delete(expense)
    await db.commit()

    return APIResponse(
        message="Expense deleted successfully.",
        data=expense
    )
