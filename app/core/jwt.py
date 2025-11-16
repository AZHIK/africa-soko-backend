from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


# ------------------------------------------------------------
# ACCESS TOKEN (short-lived)
# ------------------------------------------------------------
def create_access_token(user_id: int, is_admin: bool) -> str:
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


# ------------------------------------------------------------
# REFRESH TOKEN (long-lived)
# ------------------------------------------------------------
def create_refresh_token(user_id: int, is_admin: bool) -> str:
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


# ------------------------------------------------------------
# Decode ANY token (access or refresh)
# ------------------------------------------------------------
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
