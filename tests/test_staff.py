
import pytest


global_looped = pytest.mark.asyncio

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
    staff_data = [{
        "name": None,
        "time":10,
        "age":"test",
        "privilege": True,
        "role": 10,
    },
    {
        "name": "",
        "age": -1,
        "monthly_wage": -1,
        "role": "",
    }]

    
    for staff in staff_data:
        response = await unauth_client.post(
            path,
            json=staff,
            headers=auth_api_key,
        )
        assert response.status_code == 422

@global_looped
async def test_post_staff(unauth_client, auth_api_key):
    staff_data = {
        "name": "test staff",
        "age": 18,
        "monthly_wage": 10,
        "role": "staff",
    }

    response = await unauth_client.post(
        path,
        json=staff_data,
        headers=auth_api_key,
    )
    
    assert response.status_code == 201

    response = await unauth_client.post(
        path,
        json=staff_data,
        headers=auth_api_key,
    )
    
    assert response.status_code == 409

@global_looped
async def test_get_staff(unauth_client, auth_api_key):   

    params = {
        "name": "test staff"
    }

    response = await unauth_client.get(
        path,
        params=params,
    )

    assert response.status_code == 200

@global_looped
async def test_put_staff(unauth_client):
    
    first_name = "test staff"
    last_name = "test staff 2"

    params = {
        "name" : first_name,
    }

    update_data = {
        "name": last_name,
        "age": 20,
        "monthly_wage": 0,
        "role": "staff",
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
        "age": 30,
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
async def test_patch_staff(unauth_client):
    name = "test staff 2"
    partial_update_data = {
        "name": "test staff",
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
async def test_delete_staff(unauth_client):
    name = "test staff"

    params = {
        "name": name,
    }

    response = await unauth_client.delete(
        path,
        params=params,
    )
    
    assert response.status_code == 204

@global_looped
async def test_get_staff_not_found(unauth_client):
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
async def test_put_staff_not_found(unauth_client):
    name = "not found"

    params = {
        "name": name,
    }
    
    update_data = {
        "name": "",
        "age": 18,
        "monthly_wage": 0,
        "role": "staff",
    }

    response = await unauth_client.put(
        path,
        params=params,
        json=update_data
    )

    assert response.status_code == 404

@global_looped
async def test_patch_staff_not_found(unauth_client):
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
async def test_delete_staff_not_found(unauth_client):
    name = "test staff"

    params = {
        "name": name,
    }

    response = await unauth_client.delete(
        path,
        params=params,
    )
    
    assert response.status_code == 404

   
