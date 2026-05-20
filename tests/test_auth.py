import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "company_name": "New Company",
        "email": "newuser@example.com",
        "password": "password123",
        "name": "New User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, registered_user):
    response = await client.post("/auth/register", json={
        "company_name": "Another Company",
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user):
    response = await client.post(
        "/auth/login?tenant_slug=test-company",
        json={
            "email": "test@example.com",
            "password": "password123",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, registered_user):
    response = await client.post(
        "/auth/login?tenant_slug=test-company",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_tenant(client: AsyncClient, registered_user):
    response = await client.post(
        "/auth/login?tenant_slug=nonexistent-company",
        json={
            "email": "test@example.com",
            "password": "password123",
        }
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    response = await client.get("/projects")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_protected_route_with_token(client: AsyncClient, auth_headers):
    response = await client.get("/projects", headers=auth_headers)
    assert response.status_code == 200