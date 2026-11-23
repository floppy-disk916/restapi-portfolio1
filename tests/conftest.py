
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.db import (
    insert_test_admin,
    
)

from fastapi.testclient import TestClient

from src.db import (
    async_session,
    engine,
    get_async_session,
    insert_test_admin,
    delete_test_admin,
)

global_fixture = pytest_asyncio.fixture(scope="module", loop_scope="module")

@global_fixture
async def test_app():
    async def override_get_async_session():
        async with async_session(bind=engine, expire_on_commit=False) as session:
            yield session
            await session.rollback()
    app.dependency_overrides[get_async_session] = override_get_async_session
    yield app
    app.dependency_overrides.clear()

@global_fixture
async def unauth_client(test_app):
    _base_url = "http://test"
    transport = ASGITransport(app=test_app)
    await delete_test_admin()
    await insert_test_admin()
    async with AsyncClient(transport=transport,base_url=_base_url) as c:
        yield c
    await delete_test_admin()

@global_fixture
async def auth_token(unauth_client):
    
    data = {
        "username": "admin",
        "password": "admin",
    }

    response = await unauth_client.post("/auth/login", data=data)

    json_data = response.json()
    access_token = json_data.get("access_token")

    return access_token
