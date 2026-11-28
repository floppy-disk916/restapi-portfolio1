from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import exists, delete, insert, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import settings
from .models import Admin, APIKey, Base, Staff, Item

dsn = str(settings.db_dsn)

# Enable echo and echo_pool for debugging. Default to development mode
is_echo: bool = False
if settings.mode == "dev":
    is_echo = True

# See the documentation for available options
isolation = "READ COMMITTED"

# Per connection age. For pool_recycle
per_connection_age = settings.connection_age

engine = create_async_engine(
    dsn,
    echo=is_echo,
    echo_pool=is_echo,
    isolation_level=isolation,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    pool_recycle=per_connection_age,
    max_overflow=settings.db_burst_tolerance,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def destroy_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.reflect)
        await conn.run_sync(Base.metadata.drop_all)

async def seed_test_staff():
    async with engine.begin() as conn:
        
        subquery = select(Staff).where(
            Staff.name == "test",
            Staff.role == "staff",
            Staff.age == 18,
            Staff.monthly_wage == 0,
            )

        await conn.execute(
            insert(Staff).values(
                name = "test",
                role = "staff",
                age = 18,
                monthly_wage = 0,
            )
        )

async def seed_test_item():
    async with engine.begin() as conn:
        
        item = await conn.scalar(
            select(Item).where(
                Item.name=="test",
                Item.price==1,
                Item.tax==0,
                Item.description=="a test item",
            ))

        if item is None:
            await conn.execute(
                insert(Item).values(
                name="test",
                price=1,
                tax=0,
                tags=["test"],
                description="a test item",
            ))


async def seed_test_admin():
    async with engine.begin() as conn:
        
        admin = await conn.scalar(
            select(Admin).where(
                Admin.name == "admin",
            ),
        )

        if admin is None:
            from .auth import hash_password
            hashed = hash_password("admin")
            await conn.execute(
                insert(Admin).values(
                name="admin",
                password=hashed,
                email="admin",
            ))

async def delete_test_admin():
    async with engine.begin() as conn:

        admin = await conn.scalar(
            select(Admin).where(Admin.name == "admin"),
        )
        
        api_key = await conn.scalar(
            select(APIKey).where(
                APIKey.admin_id == admin,
            )
        )

        if admin is not None:
            await conn.execute(
                delete(Admin).where(
                    Admin.name == "admin",
                )
            )

async def delete_test_staff():
    async with engine.begin() as conn:

        staff = await conn.scalar(
            select(Staff).where(Staff.name == "test"),
        )

        if staff is not None:
            await conn.execute(
                delete(Staff).where(
                    Staff.name == "test",
                )
            )

async def delete_test_item():
    async with engine.begin() as conn:

        item = await conn.scalar(
            select(Item).where(Item.name == "test"),
        )
       
        if item is not None:
            await conn.execute(
                delete(Item).where(
                    Item.name == "test",
                )
            )


async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
        await session.commit()

ASesDep = Annotated[AsyncSession, Depends(get_async_session)]

