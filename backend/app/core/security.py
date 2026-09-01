from pwdlib import PasswordHash
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, settings.JWT_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_identifier: str | None = payload.get("sub")
        if user_identifier is None:
            return None
        return user_identifier
    except JWTError:
        return None
