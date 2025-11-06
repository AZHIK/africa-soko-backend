import asyncio
from datetime import datetime
from sqlmodel import select
import getpass
import os
from dotenv import load_dotenv
import re


from app.models.user import Role, User, UserRoleLink
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker


# Email validation regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

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


async def create_super_admin():
    async with ScriptSessionLocal() as session:
        print("=== Super Admin Setup ===")
        while True:
            email = input("Admin Email: ").strip()
            if EMAIL_REGEX.match(email):
                break
            else:
                print("Invalid email format. Please try again.")

        while True:
            username = input("Admin Username: ").strip()
            existing_username = await session.exec(
                select(User).where(User.username == username)
            )
            if existing_username.first():
                print(
                    f"Username '{username}' already exists. Please choose a different username."
                )
            else:
                break

        while True:
            password = getpass.getpass("Admin Password (hidden): ").strip()
            confirm_password = getpass.getpass("Confirm Password: ").strip()
            if password == confirm_password:
                break
            print("Passwords do not match. Please try again.")

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
                created_at=datetime.now(),
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            # Link to admin role
            admin_role_result = await session.exec(
                select(Role).where(Role.name == "admin")
            )
            admin_role = admin_role_result.first()

            if not admin_role:
                print(
                    "Error: 'admin' role not found. Please ensure roles are seeded first."
                )
                await session.rollback()
                return

            session.add(UserRoleLink(user_id=admin_user.id, role_id=admin_role.id))
            await session.commit()
            print(f"Admin user created successfully: {email}")

    await script_engine.dispose()
    print("Super admin creation script finished.")


if __name__ == "__main__":
    asyncio.run(create_super_admin())
