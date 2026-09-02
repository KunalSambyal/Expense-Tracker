from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import async_engine
from app.db.base import Base

from app.models.user import User
from app.models.category import Category
from app.models.expense import Expense

from app.api.v1.endpoints.auth import auth_router
from app.api.v1.endpoints.users import users_router
from app.api.v1.endpoints.categories import category_router
from app.api.v1.endpoints.expenses import expenses_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield


app = FastAPI(title="Expense Tracker API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(category_router)
app.include_router(expenses_router)
