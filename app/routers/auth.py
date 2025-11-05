from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead, UserLogin, Token, GoogleLogin
from app.core.security import get_password_hash, verify_password
from app.core.jwt import create_access_token, decode_access_token
from app.db.session import get_session
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Signup endpoint
@router.post("/signup", response_model=UserRead)
async def signup(user: UserCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.is_admin:
        raise HTTPException(status_code=403, detail="Cannot create admin user")

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_admin=user.is_admin,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


# Admin creation endpoint (only for existing admins)
@router.post("/admin-create", response_model=UserRead)
async def create_admin(
    user: UserCreate,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    payload = decode_access_token(token)
    if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await session.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_admin=True,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


# Login endpoint
@router.post("/login", response_model=Token)
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(user_id=db_user.id, is_admin=db_user.is_admin)
    return {"access_token": access_token, "token_type": "bearer"}


# Google OAuth login
@router.post("/login/google", response_model=Token)
async def login_google(
    payload: GoogleLogin, session: AsyncSession = Depends(get_session)
):
    async with AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.token}"
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google token")

        user_info = response.json()
        email = user_info.get("email")
        username = user_info.get("name")

        result = await session.execute(select(User).where(User.email == email))
        db_user = result.scalars().first()

        if not db_user:
            db_user = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(
                    settings.GOOGLE_USER_DEFAULT_PASSWORD
                ),
                is_admin=False,
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

        access_token = create_access_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )
        return {"access_token": access_token, "token_type": "bearer"}


# Get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
