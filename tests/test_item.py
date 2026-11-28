
import pytest


global_looped = pytest.mark.asyncio

path = "/api/v1/item/"

@global_looped
async def test_post_item_unauthorized(unauth_client):
    json_data = {}

    response = await unauth_client.post(
        path,
        json=json_data,
    )

    assert response.status_code == 401

@global_looped
async def test_delete_item_unauthorized(unauth_client):
    params = {
        "name": "test item"
    }

    response = await unauth_client.delete(
        path,
        params=params,
    )

    assert response.status_code == 401

@global_looped
async def test_post_item_invalid_data(unauth_client, auth_token):
    item_data = [{
        "name": 2,
        "tags": "test",
        "description": True,
        "price": 0,
        "tax": 2,
    },
    {
        "name": "",
        "tags": [],
        "description": [],
        "price": 0,
        "tax": 1,
    }]

    for item in item_data:
        response = await unauth_client.post(
            path,
            json=item,
            headers=auth_token,
        )
        assert response.status_code == 422

@global_looped
async def test_post_item(unauth_client, auth_token):
    item_data = {
        "name": "test item",
        "tags": ["test 1", "test 2"],
        "description": "simply a test description",
        "price": 10,
        "tax": 2,
    }

    response = await unauth_client.post(
        path,
        json=item_data,
        headers=auth_token,
    )
    
    assert response.status_code == 201

    response = await unauth_client.post(
        path,
        json=item_data,
        headers=auth_token,
    )
    
    assert response.status_code == 409

@global_looped
async def test_get_item(unauth_client, auth_token):   

    params = {
        "name": "test item"
    }

    response = await unauth_client.get(
        path,
        params=params,
    )

    assert response.status_code == 200

@global_looped
async def test_put_item(unauth_client):
    
    first_name = "test item"
    last_name = "test item 2"

    params = {
        "name" : first_name,
    }

    update_data = {
        "name": last_name,
        "tags": ["a", "b"],
        "description": "just another description",
        "price": 10,
        "tax": 0,
    }

    response = await unauth_client.put(
        path,
        params=params,
        json=update_data,
    )

    json_data = response.json()
    json_data.pop("id")

    assert response.status_code == 200
    assert json_data == update_data
    
    partial_update_data = {
        "price": 100000000,
    }

    params = {
        "name":  last_name,
    }

    response = await unauth_client.put(
        path,
        params=params,
        json=partial_update_data,
    )

    assert response.status_code == 400

@global_looped
async def test_patch_item(unauth_client):
    name = "test item 2"
    partial_update_data = {
        "name": "test item",
    }
    
    params = {
        "name": name,
    }

    response = await unauth_client.patch(
        path,
        params=params,
        json=partial_update_data,
    )

    assert response.status_code == 200

@global_looped
async def test_delete_item(unauth_client, auth_token):
    name = "test item"

    params = {
        "name": name,
    }

    response = await unauth_client.delete(
        path,
        params=params,
        headers=auth_token,
    )
    
    assert response.status_code == 204

@global_looped
async def test_get_item_not_found(unauth_client):
    name = "not found"

    params = {
        "name": name,
    }
        
    response = await unauth_client.get(
        path,
        params=params,
    )

    assert response.status_code == 404

@global_looped
async def test_put_item_not_found(unauth_client):
    name = "not found"

    params = {
        "name": name,
    }
    
    update_data = {
        "name": "name",
        "tags": [],
        "description": "description",
        "price": 10,
        "tax": 0,
    }

    response = await unauth_client.put(
        path,
        params=params,
        json=update_data
    )

    assert response.status_code == 404

@global_looped
async def test_patch_item_not_found(unauth_client):
    name = "not found"

    params = {
        "name": name,
    }
    
    update_data = {}

    response = await unauth_client.patch(
        path,
        params=params,
        json=update_data
    )

    assert response.status_code == 404

@global_looped
async def test_delete_item_not_found(unauth_client, auth_token):
    name = "test item"

    params = {
        "name": name,
    }

    response = await unauth_client.delete(
        path,
        params=params,
        headers=auth_token,
    )
    
    assert response.status_code == 404

   
