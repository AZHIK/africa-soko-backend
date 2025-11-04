# app/seeders/rbac_seeder.py
import asyncio
from datetime import datetime
from sqlmodel import select

from app.models.user import Role, Permission, RolePermissionLink, User, UserRoleLink
from app.db.session import AsyncSessionLocal as async_session_maker, engine
from app.core.security import get_password_hash


# ---- DEFINE DEFAULT PERMISSIONS ----
PERMISSIONS = [
    # Users
    {"name": "View Users", "code": "user:view"},
    {"name": "Create Users", "code": "user:create"},
    {"name": "Update Users", "code": "user:update"},
    {"name": "Delete Users", "code": "user:delete"},
    # Products
    {"name": "View Products", "code": "product:view"},
    {"name": "Create Products", "code": "product:create"},
    {"name": "Update Products", "code": "product:update"},
    {"name": "Delete Products", "code": "product:delete"},
    # Orders
    {"name": "View Orders", "code": "order:view"},
    {"name": "Create Orders", "code": "order:create"},
    {"name": "Update Orders", "code": "order:update"},
    {"name": "Delete Orders", "code": "order:delete"},
    # Vendors
    {"name": "Manage Vendors", "code": "vendor:manage"},
    # Reviews & Comments
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
    "admin": [p["code"] for p in PERMISSIONS],  # all permissions
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
        # Create Permissions
        for perm in PERMISSIONS:
            existing = await session.exec(
                select(Permission).where(Permission.code == perm["code"])
            )
            if not existing.first():
                session.add(Permission(**perm))
        await session.commit()
        print("Permissions seeded")

        # Create Roles
        for role in ROLES:
            existing = await session.exec(select(Role).where(Role.name == role["name"]))
            if not existing.first():
                session.add(Role(**role))
        await session.commit()
        print("Roles seeded")

        # Link Roles ↔ Permissions
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

        # Create Super Admin User
        admin_email = "admin@example.com"
        result = await session.exec(select(User).where(User.email == admin_email))
        if not result.first():
            hashed_pw = get_password_hash("admin123")
            admin_user = User(
                email=admin_email,
                username="admin",
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
            print("Admin user created: admin@example.com / admin123")
        else:
            print("ℹAdmin user already exists")

    await engine.dispose()
    print("RBAC seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_rbac())
