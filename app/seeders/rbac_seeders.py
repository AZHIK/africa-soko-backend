import asyncio
from sqlmodel import select
import os
from dotenv import load_dotenv

from app.models.user import Role, Permission, RolePermissionLink
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file.
load_dotenv()

# Manually construct the database URL from environment variables.
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_DB = os.getenv("POSTGRES_DB")

# Check if all required environment variables are set
if not all([PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB]):
    print("Error: Missing one or more required PostgreSQL environment variables.")
    print(
        "Please ensure POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, and POSTGRES_DB are set in your .env file."
    )
    exit(1)

DATABASE_URL = (
    f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
)

# Create a new engine and session maker for this script
script_engine = create_async_engine(DATABASE_URL, echo=False)
ScriptSessionLocal = sessionmaker(
    bind=script_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


# ---- DEFINE DEFAULT PERMISSIONS ----
PERMISSIONS = [
    {"name": "View Users", "code": "user:view"},
    {"name": "Create Users", "code": "user:create"},
    {"name": "Update Users", "code": "user:update"},
    {"name": "Delete Users", "code": "user:delete"},
    {"name": "View Products", "code": "product:view"},
    {"name": "Create Products", "code": "product:create"},
    {"name": "Update Products", "code": "product:update"},
    {"name": "Delete Products", "code": "product:delete"},
    {"name": "View Orders", "code": "order:view"},
    {"name": "Create Orders", "code": "order:create"},
    {"name": "Update Orders", "code": "order:update"},
    {"name": "Delete Orders", "code": "order:delete"},
    {"name": "Manage Vendors", "code": "vendor:manage"},
    {"name": "Add Review", "code": "review:create"},
    {"name": "Moderate Review", "code": "review:moderate"},
]

# ---- DEFINE DEFAULT ROLES ----
ROLES = [
    {"name": "admin", "description": "Full system administrator"},
    {"name": "vendor", "description": "Store owner/vendor"},
    {"name": "customer", "description": "Regular shopper"},
]

# ---- MAP ROLE PERMISSIONS ----
ROLE_PERMISSIONS = {
    "admin": [p["code"] for p in PERMISSIONS],
    "vendor": [
        "product:view",
        "product:create",
        "product:update",
        "order:view",
        "review:create",
    ],
    "customer": [
        "product:view",
        "order:create",
        "review:create",
    ],
}


async def seed_rbac():
    async with ScriptSessionLocal() as session:
        # Check if RBAC has already been seeded
        existing_admin_role = await session.exec(
            select(Role).where(Role.name == "admin")
        )
        if existing_admin_role.first():
            print("RBAC roles and permissions already exist. Skipping seeding.")
            await script_engine.dispose()
            return

        # ---- SEED PERMISSIONS ----
        for perm in PERMISSIONS:
            existing = await session.exec(
                select(Permission).where(Permission.code == perm["code"])
            )
            if not existing.first():
                session.add(Permission(**perm))
        await session.commit()
        print("Permissions seeded")

        # ---- SEED ROLES ----
        for role in ROLES:
            existing = await session.exec(select(Role).where(Role.name == role["name"]))
            if not existing.first():
                session.add(Role(**role))
        await session.commit()
        print("Roles seeded")

        # ---- LINK ROLES TO PERMISSIONS ----
        roles = (await session.exec(select(Role))).all()
        perms = (await session.exec(select(Permission))).all()

        perm_dict = {p.code: p for p in perms}
        role_dict = {r.name: r for r in roles}

        for role_name, perm_codes in ROLE_PERMISSIONS.items():
            role = role_dict[role_name]
            for code in perm_codes:
                perm = perm_dict.get(code)
                if not perm:
                    continue
                existing_link = await session.exec(
                    select(RolePermissionLink)
                    .where(RolePermissionLink.role_id == role.id)
                    .where(RolePermissionLink.permission_id == perm.id)
                )
                if not existing_link.first():
                    session.add(
                        RolePermissionLink(role_id=role.id, permission_id=perm.id)
                    )
        await session.commit()
        print("Role ↔ Permission links created")

        await script_engine.dispose()
    print("RBAC seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_rbac())
