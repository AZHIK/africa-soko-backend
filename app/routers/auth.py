# new authenticate endpoint to match frontend fetch
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from httpx import AsyncClient
from datetime import datetime

from app.models.user import Role, User, UserRoleLink
from app.core.security import get_password_hash, verify_password
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
)  # see note below
from app.db.session import get_session
from app.core.config import settings

router = APIRouter(tags=["auth"])
security_scheme = HTTPBearer()


@router.post("")
async def authenticate(
    request: Request, response: Response, session: AsyncSession = Depends(get_session)
):
    """
    Accepts JSON:
      { auth_type: str, auth_by: str | dict, referee: Optional[str] }

    Behaviour:
      - If auth_type == "google" OR auth_by looks like an ID token (contains two dots),
        treat auth_by as a Google ID token and verify with Google.
      - If auth_type == "email" and auth_by is an object with email/password, perform normal email login.
      - Return JSON shaped exactly like your frontend expects.
    """
    payload = await request.json()
    auth_type = (payload.get("auth_type") or "").lower()
    auth_by = payload.get("auth_by")
    referee = payload.get("referee")

    # helper to return the exact frontend shape
    def make_response_struct(
        access_token: str, refresh_token: str, is_new: bool, role_name: str = None
    ):
        return {
            "status": "success",
            "___access_token": access_token,
            "___refresh_token": refresh_token,
            "new": is_new,
            "role": role_name,
            "referee": referee or None,
        }

    # ---------- CASE A: Google ID token path ----------
    looks_like_jwt = isinstance(auth_by, str) and auth_by.count(".") == 2
    if auth_type == "google" or looks_like_jwt:
        id_token = auth_by
        if not id_token:
            return {"status": "failed", "detail": "No Google ID token provided"}

        # verify with Google tokeninfo endpoint
        async with AsyncClient() as client:
            google_resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
                timeout=10.0,
            )

        if google_resp.status_code != 200:
            # token invalid
            return {"status": "failed", "detail": "Invalid Google ID token"}

        tinfo = google_resp.json()
        # Basic recommended checks:
        # - audience (aud) should match your CLIENT_ID in settings, if provided
        if getattr(settings, "GOOGLE_CLIENT_ID", None):
            aud = tinfo.get("aud")
            if aud != settings.GOOGLE_CLIENT_ID:
                return {"status": "failed", "detail": "Token audience does not match"}

        # Extract canonical fields
        email = tinfo.get("email")
        name = tinfo.get("name") or tinfo.get("given_name") or "Google User"
        if not email:
            return {"status": "failed", "detail": "Google token has no email"}

        # Check/create user
        result = await session.execute(select(User).where(User.email == email))
        db_user = result.scalars().first()
        is_new = False
        if not db_user:
            is_new = True
            db_user = User(
                email=email,
                username=name,
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

            # assign a default role if you have one (optional)
            default_role_name = getattr(settings, "DEFAULT_ROLE_NAME", None)
            if default_role_name:
                role_q = await session.execute(
                    select(Role).where(Role.name == default_role_name)
                )
                role = role_q.scalars().first()
                if role:
                    user_role_link = UserRoleLink(user_id=db_user.id, role_id=role.id)
                    session.add(user_role_link)
                    await session.commit()
                else:
                    role = None
            else:
                # try to get any role that may exist (or leave as None)
                role = None
        else:
            # load role if exists
            r_q = await session.execute(
                select(Role)
                .join(UserRoleLink, Role.id == UserRoleLink.role_id)
                .where(UserRoleLink.user_id == db_user.id)
            )
            role = r_q.scalars().first()

        # Create tokens (access + refresh)
        access_token = create_access_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )
        # create_refresh_token should be implemented to return a longer-lived token
        refresh_token = create_refresh_token(
            user_id=db_user.id, is_admin=db_user.is_admin
        )

        # (Optional) Set cookie for cookie-based flows if you want credentials: "include" to matter:
        # response.set_cookie("sokoni_identity", access_token, httponly=True, secure=not settings.DEBUG, samesite="lax")

        return make_response_struct(
            access_token, refresh_token, is_new, role.name if role else None
        )

    # ---------- CASE B: Email/password login path ----------
    # Accept either:
    #  - auth_by is an object like { "email": "...", "password": "..." }
    #  - or auth_by is a plain email string (in which case frontend must send password elsewhere)
    if auth_type == "email":
        # Expect object with email/password
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

        # fetch role if any
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

        return make_response_struct(
            access_token, refresh_token, False, role.name if role else None
        )

    # ---------- Unsupported auth_type ----------
    return {"status": "failed", "detail": "Unsupported auth_type"}


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
