from pydantic import BaseModel, EmailStr, SecretStr, Field, field_validator
from datetime import datetime
import uuid
import re

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        max_length=200,
        min_length=3,
        pattern=r"^\w+$",
        description="Unique username containig alpha, numeric and underscore characters between 3-200.",
        examples=["john_12", "john532"],
    )
    email: EmailStr = Field(..., description="User email address for login and notifications")
    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Strong password (8+ chars, uppercase, lowercase, digit, specialchar",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        password = v.get_secret_value()

        # Use Python's re module for full regex support (look-aheads work here)
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain a digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain a special character")

        return v

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
