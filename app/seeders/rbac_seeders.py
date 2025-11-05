import asyncio
from datetime import datetime
from sqlmodel import select
import getpass

from app.models.user import Role, Permission, RolePermissionLink, User, UserRoleLink
from app.db.session import AsyncSessionLocal as async_session_maker, engine
from app.core.security import get_password_hash

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
    async with async_session_maker() as session:
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

        # ---- CREATE SUPER ADMIN ----
        print("\n=== Super Admin Setup ===")
        email = input("Admin Email: ").strip()
        username = input("Admin Username: ").strip()

        while True:
            password = getpass.getpass("Admin Password (hidden): ").strip()
            confirm_password = getpass.getpass("Confirm Password: ").strip()
            if password == confirm_password:
                break
            print(" Passwords do not match. Please try again.\n")

        existing_user = await session.exec(select(User).where(User.email == email))
        if existing_user.first():
            print("ℹ Super admin already exists with this email.")
        else:
            hashed_pw = get_password_hash(password)
            admin_user = User(
                email=email,
                username=username,
                hashed_password=hashed_pw,
                is_active=True,
                is_admin=True,
                created_at=datetime.utcnow(),
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            # Link to admin role
            admin_role = role_dict["admin"]
            session.add(UserRoleLink(user_id=admin_user.id, role_id=admin_role.id))
            await session.commit()
            print(f"Admin user created successfully: {email}")

    await engine.dispose()
    print("\nRBAC seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_rbac())
