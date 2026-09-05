from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

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
        username = verify_access_token(token)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserService.get_by_username(db, username)

    if user is None:
        raise credentials_exception

    return user