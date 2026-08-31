from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Uuid, ForeignKey
import uuid
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expense import Expense


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="categories")
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="category", cascade="all, delete-orphan")