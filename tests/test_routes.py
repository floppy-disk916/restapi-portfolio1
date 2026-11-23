import pytest
import asyncio

loop: asyncio.AbstractEventLoop

global_looped = pytest.mark.asyncio(loop_scope="module")

@global_looped
async def test_remember_loop():
    global loop
    loop = asyncio.get_running_loop()

@global_looped
async def test_protected_routes_unauthorized(unauth_client):
    """Prove that creating an item requires authentication."""
    
    path = "/api/v1/item/"
    item_data = {
        "name": "Test Widget",
        "tags": ["test"],
        "description": "A test item",
        "price": 10.0,
        "tax": 1.0
    }
    
    delete_param = {
        'name': 'Null item',
    }

    response = await unauth_client.post(
        path,
        json=item_data,
    )
    
    # Your route requires check_current_token, so this should be 401
    assert response.status_code == 401

    response = await unauth_client.delete("/api/v1/item/", params=delete_param)

    assert response.status_code == 401

@global_looped
async def test_get_item_not_found(unauth_client):
    """Prove that fetching a non-existent item returns 404."""
    
    path = "/api/v1/item/"
    item_name = "?name=ThisDoesNotExist"
    full_path = path + item_name
    response = await unauth_client.get(
        full_path,
    )
    
    assert response.status_code == 404

@global_looped
async def test_update_item_not_found(unauth_client):
    """Prove that updating non-existent item returns 404."""

    path ="/api/v1/item/"
    params = {
        'name': 'asfhaoffhio13123',
    }

    item_data = {
            'name': 'aisfuaf133',
            'tags': [],
            'description': 'random item',
            'tax': 100,
            'price': 10000,
    }

    response = await unauth_client.put(
        path,
        params=params,
        json=item_data,
    )

    assert response.status_code == 404

@global_looped
async def test_item_protected_routes(unauth_client, auth_token):
    """
        Prove that protected routes work, 
        create_item returns 201,
        and delete_item returns 204
    """
    
    path = "/api/v1/item/"

    item_data = {
        'name': 'test_item',
        'tags': ['test'],
        'description': 'test item',
        'tax': 0,
        'price': 1000,
    }
    

    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    response = await unauth_client.post(
        path,
        headers=headers,
        json=item_data,
    )

    assert response.status_code == 201

    delete_param = {
        "name": "test_item",
    }

    response = await unauth_client.delete(
        path,
        headers=headers,
        params=delete_param,
    )

    assert response.status_code == 204
