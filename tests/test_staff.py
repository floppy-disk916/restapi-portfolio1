
import pytest


global_looped = pytest.mark.asyncio(loop_scope="module")

path = "/api/v1/staff/"

@global_looped
async def test_post_staff_unauthorized(unauth_client):
    json_data = {}

    response = await unauth_client.post(
        path,
        json=json_data,
    )

    assert response.status_code == 401

@global_looped
async def test_post_staff_invalid_data(unauth_client, auth_api_key):
    json_data = {
        "name": 0,
        "role": 0,
        "avg_wage": "test",
        "age": 0,
    }

    json_data_1 = {
        "name": 0,
        "role": 0,
        "avg_wage": "test",
        "age": "test",
    }
    


@global_looped
async def test_post_staff(unauth_client, auth_api_key):
    json_data = {
        "name": "test staff",
        "role": "staff",
        "avg_wage": 0,
        "age": 20,
    }

@global_looped
async def test_get_staff(unauth_client):
    pass

@global_looped
async def test_put_staff(unauth_client):
    pass
    
@global_looped
async def test_patch_staff(unauth_client):
    pass

@global_looped
async def test_delete_staff(unauth_client):
    pass

@global_looped
async def test_get_staff_not_found(unauth_client):
    pass

@global_looped
async def test_put_staff_not_found(unauth_client):
    pass

@global_looped
async def test_patch_staff_not_found(unauth_client):
    pass

@global_looped
async def test_delete_staff_not_found(unauth_client):
    pass
