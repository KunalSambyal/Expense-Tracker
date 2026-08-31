from pydantic import BaseModel, Field
from typing import Optional
import datetime
import uuid


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Short summary of the expense", examples=["Weekly groceries"])
    amount: float = Field(..., gt=0, description="Amount spent(Must be greater than 0)")
    description: Optional[str] = Field(default=None, description="Optional detailed note about the transaction")
    date: datetime.date = Field(..., description="Date when the transaction occurred (YYYY-MM-DD)")
    category_id: uuid.UUID = Field(..., description="UUID of the associated category")

    model_config = {"from_attributes": True}



class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = None
    date: Optional[datetime.date] = None
    category_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    title: str
    amount: float
    description: Optional[str]
    date: datetime.date
    user_id: uuid.UUID
    category_id: uuid.UUID

    model_config = {"from_attributes": True}