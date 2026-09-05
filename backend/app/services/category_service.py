from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.category import Category
from app.schemas.category import CategoryCreate

class CategoryService:

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: UUID, user_id: UUID) -> Category | None:
        query = select(Category).where(Category.id == category_id, Category.user_id == user_id)
        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str, user_id: UUID) -> Category | None:
        query = select(Category).where(Category.name == name, Category.user_id == user_id)
        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def get_all_by_user(db: AsyncSession, user_id: UUID) -> list[Category]:
        query = select(Category).where(Category.user_id == user_id)
        result = (await db.execute(query)).scalars().all()
        return result

    @staticmethod
    async def create(db: AsyncSession, category_data: CategoryCreate, user_id: UUID) -> Category:
        new_category = Category(
            name=category_data.name,
            user_id=user_id
        )
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        return new_category

    @staticmethod
    async def delete(db: AsyncSession, category: Category) -> None:
        await db.delete(category)
        await db.commit()
