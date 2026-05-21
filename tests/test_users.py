import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, auth_headers):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "name" in data
    assert "role" in data
    assert "must_change_password" in data


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers):
    response = await client.patch(
        "/users/me",
        json={"name": "Updated Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient, auth_headers):
    response = await client.post(
        "/users/me/change-password",
        json={
            "current_password": "password123",
            "new_password": "newpassword123",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, auth_headers):
    response = await client.post(
        "/users/me/change-password",
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_password_too_short(client: AsyncClient, auth_headers):
    response = await client.post(
        "/users/me/change-password",
        json={
            "current_password": "password123",
            "new_password": "short",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_forgot_password_valid_email(client: AsyncClient, registered_user):
    response = await client.post(
        "/users/forgot-password",
        json={
            "email": "test@example.com",
            "tenant_slug": "test-company",
        }
    )
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_forgot_password_invalid_email(client: AsyncClient):
    response = await client.post(
        "/users/forgot-password",
        json={
            "email": "nonexistent@example.com",
            "tenant_slug": "test-company",
        }
    )
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    response = await client.post(
        "/users/reset-password",
        json={
            "token": "invalidtoken123",
            "new_password": "newpassword123",
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_profile_shows_role(client: AsyncClient, auth_headers):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_invited_user_must_change_password(client: AsyncClient, auth_headers):
    invite_response = await client.post(
        "/workspace/invite",
        json={"email": "mustchange@example.com", "role": "member"},
        headers=auth_headers,
    )
    assert invite_response.status_code == 200
    assert invite_response.json()["user"]["must_change_password"] == True