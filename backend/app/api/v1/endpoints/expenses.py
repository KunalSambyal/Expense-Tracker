from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from datetime import date

from app.db.session import get_db, AsyncSession
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.schemas.response import APIResponse
from app.core.dependencies import get_current_user
from app.services.expense_service import ExpenseService
from app.services.category_service import CategoryService

expenses_router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])


@expenses_router.post(
    "", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_201_CREATED
)
async def add_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession=Depends(get_db),
    current_user: User=Depends(get_current_user),
):
    category = await CategoryService.get_by_id(db, expense_data.category_id, current_user.id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or does not belong to user.",
        )

    new_expense = await ExpenseService.create(db, expense_data, current_user.id)

    return APIResponse(
        code=201,
        message="Expense created successfully", 
        data=new_expense
    )


@expenses_router.get("", response_model=APIResponse[list[ExpenseResponse]], status_code=status.HTTP_200_OK)
async def get_expenses(
    category_id: uuid.UUID | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sort_by: str = "date",
    order: str = "desc",
    page: int = 1,
    page_size: int = 10,
    current_user: User=Depends(get_current_user), 
    db: AsyncSession=Depends(get_db)
):
    expenses = await ExpenseService.get_filtered_expenses(
        db=db,
        user_id=current_user.id,
        category_id=category_id,
        min_amount=max_amount,
        max_amount=max_amount,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size
    )

    return APIResponse(
        message="Expenses retrieved successfully.",
        data=expenses
    )


@expenses_router.get("/{expense_id}", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_200_OK)
async def get_expense(expense_id: uuid.UUID, current_user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    user_expense = await ExpenseService.get_by_id(db, expense_id, current_user.id)

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
    existing_expense = await ExpenseService.get_by_id(db, expense_id, current_user.id)

    if existing_expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id: {expense_id} not found"
        )

    update_data = expense_data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category_result = await CategoryService.get_by_id(db, category_id=update_data["category_id"], user_id=current_user.id)

        if not category_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or does not belong to the user"
            )
    update_expense = await ExpenseService.update(db, existing_expense, update_data)

    return APIResponse(
        message="Expense updated successfully.",
        data=update_expense
    )


@expenses_router.delete("/{expense_id}", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_200_OK)
async def delete_expense(expense_id: uuid.UUID, db: AsyncSession=Depends(get_db), current_user: User=Depends(get_current_user)):
    expense = await ExpenseService.get_by_id(db, expense_id, current_user.id)

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id: {expense_id} not found"
        )

    await ExpenseService.delete(db, expense)

    return APIResponse(
        message="Expense deleted successfully.",
        data=expense
    )
