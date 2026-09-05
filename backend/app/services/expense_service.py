from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate

class ExpenseService:

    @staticmethod
    async def get_by_id(db: AsyncSession, expense_id: UUID, user_id: UUID) -> Expense | None:
        query = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def get_all_by_user(db: AsyncSession, user_id: UUID) -> list[Expense]:
        query = select(Expense).where(Expense.user_id == user_id)
        result = (await db.execute(query)).scalars().all()
        return result

    @staticmethod
    async def get_filtered_expenses(
        db: AsyncSession, 
        user_id: UUID, 
        category_id: UUID | None = None, 
        min_amount: float | None = None, 
        max_amount: float | None = None, 
        start_date=None, 
        end_date=None, 
        sort_by: str = "date", 
        order: str = "desc", 
        page: int = 1, 
        page_size: int = 10
    ) -> list[Expense]:
        query = select(Expense).where(Expense.user_id == user_id)

        if category_id is not None:
            query = query.where(Expense.category_id == category_id)
        if min_amount is not None:
            query = query.where(Expense.amount >= min_amount)
        if max_amount is not None:
            query = query.where(Expense.amount <= max_amount)
        if start_date is not None:
            query = query.where(Expense.date >= start_date)
        if end_date is not None:
            query = query.where(Expense.date <= end_date)

        sort_fields = {
            "date": Expense.date,
            "amount": Expense.amount,
            "title": Expense.title
        }
        sort_col = sort_fields.get(sort_by, Expense.date)

        if order.lower() == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, expense_data: ExpenseCreate, user_id: UUID) -> Expense:
        new_expense = Expense(**expense_data.model_dump(), user_id=user_id)
        db.add(new_expense)
        await db.commit()
        await db.refresh(new_expense)
        return new_expense

    @staticmethod
    async def update(db: AsyncSession, expense: Expense, update_data: dict) -> Expense:
        for field, value in update_data.items():
            setattr(expense, field, value)
        await db.commit()
        await db.refresh(expense)
        return expense

    @staticmethod
    async def delete(db: AsyncSession, expense: Expense) -> None:
        await db.delete(expense)
        await db.commit()
