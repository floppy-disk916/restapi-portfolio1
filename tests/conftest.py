from src.db import (
    AsyncSession,
    async_sessionmaker,
    engine,
    get_async_session,
    async_session,
)

from src.schemas import Token
from src.app import app

from fastapi import FastAPI
from collections.abc import AsyncGenerator


from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio

@pytest_asyncio.fixture(scope="module")
async def test_app():
    async def override_get_async_session():
        async with async_session(bind=engine, expire_on_commit=False) as session:
            yield session
            await session.rollback()
    app.dependency_overrides[get_async_session] = override_get_async_session
    yield app
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="module")
async def unauth_client(test_app):
    _base_url = "http://test"
    _transport = ASGITransport(app=test_app)
    return AsyncClient(transport=_transport, base_url=_base_url)


