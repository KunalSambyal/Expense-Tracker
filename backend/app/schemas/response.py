from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    succsess: bool = True
    code: int = 200
    message: str = "Operation successful"
    data: Optional[T] = None
