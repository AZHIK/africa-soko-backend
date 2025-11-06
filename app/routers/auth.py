from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from httpx import AsyncClient
from datetime import datetime

from app.models.user import Role, User, UserRoleLink
from app.schemas.user_schema import UserCreate, UserRead, UserLogin, Token, GoogleLogin
from app.core.security import get_password_hash, verify_password
from app.core.jwt import create_access_token, decode_access_token
from app.db.session import get_session
from app.core.config import settings

# -------------------------------------------------------------------------
# Router and Security Scheme
# -------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer()


# -------------------------------------------------------------------------
# Signup endpoint
# -------------------------------------------------------------------------
@router.post("/signup", response_model=UserRead)
async def signup(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    # Check if user exists
    result = await session.execute(select(User).where(User.email == user_data.email))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pw,
        is_active=True,
        is_admin=False,
        created_at=datetime.now(),
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Assign default or chosen role
    role_result = await session.execute(
        select(Role).where(Role.name == user_data.role_name)
    )
    role = role_result.scalars().first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role")

    user_role_link = UserRoleLink(user_id=new_user.id, role_id=role.id)
    session.add(user_role_link)
    await session.commit()

    return UserRead(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        is_admin=new_user.is_admin,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        role_name=role.name,
    )


# -------------------------------------------------------------------------
# Admin creation endpoint (requires admin JWT)
# -------------------------------------------------------------------------
@router.post("/admin-create", response_model=UserRead)
async def create_admin(
    user: UserCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if user already exists
    result = await session.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create admin user
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


# -------------------------------------------------------------------------
# Login endpoint
# -------------------------------------------------------------------------
@router.post("/login", response_model=Token)
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(user_id=db_user.id, is_admin=db_user.is_admin)
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------------------------------------------------------
# Google OAuth login
# -------------------------------------------------------------------------
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


# -------------------------------------------------------------------------
# Get current user
# -------------------------------------------------------------------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
