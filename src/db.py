from .config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fastapi import Depends
from typing import Annotated
from collections.abc import AsyncGenerator

dsn = str(settings.db_dsn)

#Enable echo and echo_pool for debugging. Default to development mode
is_echo: bool = True
if settings.mode == "prod":
    is_echo = False

#See the documentation for available options
isolation="READ COMMITTED"

#Per connection age. For pool_recycle
per_connection_age=3600

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

async_session = async_sessionmaker(engine)

async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
        session.commit()

ASesDep = Annotated[AsyncSession, Depends(get_async_session)]
