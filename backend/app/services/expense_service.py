from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import HTTPException
import datetime

from app.models.category import Category
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
        try:
            new_expense = Expense(**expense_data.model_dump(), user_id=user_id)
            db.add(new_expense)
            await db.commit()
            await db.refresh(new_expense)
            return new_expense
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Invalid category or user reference for this expense."
            )

    @staticmethod
    async def update(db: AsyncSession, expense: Expense, update_data: dict) -> Expense:
        try:
            for field, value in update_data.items():
                setattr(expense, field, value)
            await db.commit()
            await db.refresh(expense)
            return expense
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Failed to update expense: referenced category doed not exists."
            )

    @staticmethod
    async def delete(db: AsyncSession, expense: Expense) -> None:
        await db.delete(expense)
        await db.commit()

    @staticmethod
    async def get_summary(db: AsyncSession, user_id: UUID):
        total_query = select(func.coalesce(func.sum(Expense.amount), 0.0)).where(Expense.user_id == user_id)
        total_spending = float((await db.execute(total_query)).scalar_one())

        first_day_of_month = datetime.date.today().replace(day=1)

        month_query = select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
            Expense.user_id == user_id, 
            Expense.date >= first_day_of_month
        )
        month_spending = float((await db.execute(month_query)).scalar_one())

        cat_query = (
            select(Category.name, func.coalesce(func.sum(Expense.amount), 0.0)).join(
                Category, Expense.category_id == Category.id
            ).where(
                Expense.user_id == user_id
            ).group_by(Category.name)
        )
        cat_rows = (await db.execute(cat_query)).all()
        by_category = []
        for cat_name, cat_total in cat_rows:
            amount = float(cat_total)
            percentage = round((amount / total_spending * 100), 2) if total_spending > 0 else 0.0

            by_category.append({
                "category_name": cat_name,
                "total_amount": round(amount, 2),
                "percentage": percentage
            })

        return {
            "total_spending": round(total_spending, 2),
            "current_month_spending": round(month_spending, 2),
            "by_category": by_category,
            "ai_insight": None
        }

