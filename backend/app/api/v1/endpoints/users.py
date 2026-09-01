from fastapi import APIRouter, status, Depends

from app.schemas.response import APIResponse
from app.schemas.user import UserResponse
from app.models.user import User
from app.core.dependencies import get_current_user

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.get("/me", response_model=APIResponse[UserResponse], status_code=status.HTTP_200_OK)
async def get_user(current_user: User = Depends(get_current_user)):
    return APIResponse(
        message="User retrieved successfully",
        data=current_user
    )
