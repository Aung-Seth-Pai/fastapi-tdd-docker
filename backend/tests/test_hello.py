# backend/tests/test_hello.py

from app import main

# define test for /hello endpoint that uses our conftest fixture
async def test_hello(async_client):
    response = await async_client.get("/api/hello")
    assert response.status_code == 200
    data = response.json()
    assert data["hello"] == "world"
    assert data["app_name"] == "My App"
    assert data["environment"] == "dev"
    assert data["testing"] == 1
    
async def test_async_hello(async_client):
    response = await async_client.get("/api/async_hello")
    assert response.status_code == 200
    data = response.json()
    assert data["hello"] == "world"
    assert data["app_name"] == "My App"
    assert data["environment"] == "dev"
    assert data["testing"] == 1
    assert data["db_url"] == "postgres://postgres:password@db:5432/web_test"