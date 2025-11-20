from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from httpx import AsyncClient
from datetime import datetime

from app.models.user import Role, User, UserRoleLink
from app.core.security import get_password_hash, verify_password
from app.core.jwt import create_access_token, create_refresh_token, decode_access_token
from app.db.session import get_session
from app.core.config import settings
from app.schemas.auth_schema import (
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    EmailLoginRequest,
    UserCreate,
    UserRead,
)

router = APIRouter(tags=["auth"])
security_scheme = HTTPBearer()


def make_frontend_response(
    access_token: str,
    refresh_token: str,
    is_new: bool,
    role_name: str = None,
    referee: str = None,
):
    return {
        "status": "success",
        "___access_token": access_token,
        "___refresh_token": refresh_token,
        "new": is_new,
        "role": role_name,
        "referee": referee,
    }


@router.post("")
async def authenticate(
    request: Request, response: Response, session: AsyncSession = Depends(get_session)
):
    """
    Handles:
      - Google login (ID token)
      - Email/password login
      - Refresh token exchange (if included)
    """
    payload = await request.json()
    auth_type = (payload.get("auth_type") or "").lower()
    auth_by = payload.get("auth_by")
    referee = payload.get("referee")

    looks_like_jwt = isinstance(auth_by, str) and auth_by.count(".") == 2
    if auth_type == "email" and looks_like_jwt:
        id_token = auth_by
        if not id_token:
            return {"status": "failed", "detail": "No Google ID token provided"}

        # Verify token with Google
        async with AsyncClient() as client:
            google_resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
                timeout=10.0,
            )
        if google_resp.status_code != 200:
            return {"status": "failed", "detail": "Invalid Google ID token"}

        tinfo = google_resp.json()
        if getattr(settings, "GOOGLE_CLIENT_ID", None):
            if tinfo.get("aud") != settings.GOOGLE_CLIENT_ID:
                return {"status": "failed", "detail": "Token audience does not match"}

        email = tinfo.get("email")
        username = tinfo.get("name") or tinfo.get("given_name") or "Google User"
        if not email:
            return {"status": "failed", "detail": "Google token has no email"}

        # Check if user exists
        result = await session.execute(select(User).where(User.email == email))
        db_user = result.scalars().first()
        is_new = False
        if not db_user:
            is_new = True
            db_user = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(
                    settings.GOOGLE_USER_DEFAULT_PASSWORD
                ),
                is_active=True,
                is_admin=False,
                created_at=datetime.utcnow(),
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

            # Assign default role
            default_role_name = getattr(settings, "DEFAULT_ROLE_NAME", None)
            if default_role_name:
                role_q = await session.execute(
                    select(Role).where(Role.name == default_role_name)
                )
                role = role_q.scalars().first()
                if role:
                    session.add(UserRoleLink(user_id=db_user.id, role_id=role.id))
                    await session.commit()
            else:
                role = None
        else:
            r_q = await session.execute(
                select(Role)
                .join(UserRoleLink, Role.id == UserRoleLink.role_id)
                .where(UserRoleLink.user_id == db_user.id)
            )
            role = r_q.scalars().first()

        access_token = create_access_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )
        refresh_token = create_refresh_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )

        return make_frontend_response(
            access_token, refresh_token, is_new, role.name if role else None, referee
        )

    if auth_type == "email":
        if not isinstance(auth_by, dict):
            return {
                "status": "failed",
                "detail": "For email auth provide { email, password } in auth_by",
            }

        email = auth_by.get("email")
        password = auth_by.get("password")
        if not email or not password:
            return {"status": "failed", "detail": "Missing email or password"}

        result = await session.execute(select(User).where(User.email == email))
        db_user = result.scalars().first()
        if not db_user or not verify_password(password, db_user.hashed_password):
            return {"status": "failed", "detail": "Invalid credentials"}

        # Load role
        r_q = await session.execute(
            select(Role)
            .join(UserRoleLink, Role.id == UserRoleLink.role_id)
            .where(UserRoleLink.user_id == db_user.id)
        )
        role = r_q.scalars().first()

        access_token = create_access_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )
        refresh_token = create_refresh_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )

        return make_frontend_response(
            access_token, refresh_token, False, role.name if role else None, referee
        )

    if auth_type == "refresh":
        refresh_token = auth_by
        if not refresh_token:
            return {"status": "failed", "detail": "No refresh token provided"}

        try:
            payload = decode_access_token(refresh_token)
            user_id = int(payload.get("sub"))
        except Exception:
            return {"status": "failed", "detail": "Invalid refresh token"}

        result = await session.execute(select(User).where(User.id == user_id))
        db_user = result.scalars().first()
        if not db_user:
            return {"status": "failed", "detail": "User not found"}

        r_q = await session.execute(
            select(Role)
            .join(UserRoleLink, Role.id == UserRoleLink.role_id)
            .where(UserRoleLink.user_id == db_user.id)
        )
        role = r_q.scalars().first()

        new_access_token = create_access_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )
        return make_frontend_response(
            new_access_token, refresh_token, False, role.name if role else None, referee
        )
    return {"status": "failed", "detail": "Unsupported auth_type"}


@router.post("/login-email", response_model=LoginResponse)
async def login_with_email(
    data: EmailLoginRequest,
    session: AsyncSession = Depends(get_session),
):
    # Get user by email
    result = await session.execute(select(User).where(User.email == data.email))
    db_user = result.scalars().first()

    if not db_user or not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Load user role
    r_q = await session.execute(
        select(Role)
        .join(UserRoleLink, Role.id == UserRoleLink.role_id)
        .where(UserRoleLink.user_id == db_user.id)
    )
    role = r_q.scalars().first()

    # Create tokens
    access_token = create_access_token(user_id=db_user.id, is_admin=db_user.is_admin)
    refresh_token = create_refresh_token(user_id=db_user.id, is_admin=db_user.is_admin)

    return {
        "___access_token": access_token,
        "___refresh_token": refresh_token,
        "role": role.name if role else None,
        "is_new": False,
    }


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


@router.post("/refresh_token", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest, session: AsyncSession = Depends(get_session)
):
    try:
        payload = decode_access_token(request.refresh_token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token(
        user_id=db_user.id, is_admin=db_user.is_admin
    )
    # Optionally issue a new refresh token
    new_refresh_token = create_refresh_token(
        user_id=db_user.id, is_admin=db_user.is_admin
    )

    return RefreshTokenResponse(
        ___access_token=new_access_token, ___refresh_token=new_refresh_token
    )


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
