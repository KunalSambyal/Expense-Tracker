from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from uuid import UUID

from app.db.session import get_db
from app.core.security import verify_access_token
from app.models.user import User
from app.services.user_service import UserService

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_bearer), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id_str = verify_access_token(token)
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserService.get_by_id(db, UUID(user_id_str))

    if user is None:
        raise credentials_exception

    return user