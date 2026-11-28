
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.db import (
    async_session,
    delete_test_admin,
    destroy_db,
    engine,
    get_async_session,
    init_db,
    insert_test_admin,
)
from src.config import settings

from src.main import app

global_fixture = pytest_asyncio.fixture(scope="module")


@global_fixture
async def test_app():
    async def override_get_async_session():
        async with async_session(bind=engine, expire_on_commit=False) as session:
            yield session
            await session.rollback()
    app.dependency_overrides[get_async_session] = override_get_async_session
    yield app
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="module", autouse=True)
async def unauth_client(test_app):
    """
        Setting up test client with temporary mock database environment.
        This is done because the create methods in database repository
        commit insertions permanently.
        So by making the database temporary, the mock data won't pollute the
        database
    """

    _base_url = "http://test"
    transport = ASGITransport(app=test_app)

    await destroy_db()
    await init_db()
    
    await insert_test_admin()
    async with AsyncClient(transport=transport,base_url=_base_url) as c:
        yield c
    
    await delete_test_admin()
    await destroy_db()

@pytest_asyncio.fixture(scope="function")
async def auth_token(unauth_client):
    """Setting up the auth token for protected route testing"""
    data = {
        "username": "admin",
        "password": "admin",
    }

    response = await unauth_client.post("/auth/login", data=data)

    json_data = response.json()
    access_token = json_data.get("access_token")

    return {"Authorization": f"Bearer {access_token} "}

@pytest_asyncio.fixture(scope="module")
async def auth_api_key(unauth_client):
    data = {
        "name": "admin",
        "password": "admin",
        "email": "admin@mail.com",
    }

    response = await unauth_client.post("/admin/register", data=data)
    
    
    return {"X-API-Key":f"{response.json()}"}

