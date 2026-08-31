from pydantic import BaseModel, Field
import uuid


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the expense category", examples=["Groceries", "Utilities", "Entertainment"])

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID

    model_config = {"from_attributes": True}