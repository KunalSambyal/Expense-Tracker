import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password_hash

class UserService:
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def get_by_username_or_email(db: AsyncSession, username: str, email: str) -> User | None:
        query = select(User).where(or_(
            User.username == username,
            User.email == email
        ))
        result = (await db.execute(query)).scalar_one_or_none()
        return result

    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> User:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password.get_secret_value())
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
        user = await UserService.get_by_username(db, username)
        if not user or not verify_password_hash(password, user.password_hash):
            return None
        return user
