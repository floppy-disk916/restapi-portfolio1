import pytest
from src.schemas import ItemAdd

@pytest.mark.asyncio
async def test_create_item_unauthorized(unauth_client):
    """Prove that creating an item requires authentication."""
    item_data = {
        "name": "Test Widget",
        "tags": ["test"],
        "description": "A test item",
        "price": 10.0,
        "tax": 1.0
    }
    
    response = await unauth_client.post("/api/v1/item/", json=item_data)
    
    # Your route requires check_current_token, so this should be 401
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_item_not_found(unauth_client):
    """Prove that fetching a non-existent item returns 404."""
    response = await unauth_client.get("/api/v1/item/?name=ThisDoesNotExist")
    
    assert response.status_code == 404
