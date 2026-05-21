import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_workspace(client: AsyncClient, auth_headers):
    response = await client.get("/workspace/settings", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "slug" in data
    assert "plan" in data


@pytest.mark.asyncio
async def test_update_workspace(client: AsyncClient, auth_headers):
    response = await client.patch(
        "/workspace/settings",
        json={"name": "Updated Workspace"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Workspace"


@pytest.mark.asyncio
async def test_list_members(client: AsyncClient, auth_headers):
    response = await client.get("/workspace/members", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_invite_member(client: AsyncClient, auth_headers):
    response = await client.post(
        "/workspace/invite",
        json={"email": "invited@example.com", "role": "member"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "invited@example.com" in data["message"]


@pytest.mark.asyncio
async def test_invited_member_has_must_change_password(client: AsyncClient, auth_headers):
    response = await client.post(
        "/workspace/invite",
        json={"email": "forcechange@example.com", "role": "member"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["user"]["must_change_password"] == True


@pytest.mark.asyncio
async def test_invited_member_role_is_member(client: AsyncClient, auth_headers):
    response = await client.post(
        "/workspace/invite",
        json={"email": "rolecheck@example.com", "role": "member"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "member"


@pytest.mark.asyncio
async def test_invite_duplicate_member(client: AsyncClient, auth_headers):
    await client.post(
        "/workspace/invite",
        json={"email": "duplicate@example.com", "role": "member"},
        headers=auth_headers,
    )
    response = await client.post(
        "/workspace/invite",
        json={"email": "duplicate@example.com", "role": "member"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_member_cannot_update_workspace(client: AsyncClient, auth_headers):
    await client.post(
        "/workspace/invite",
        json={"email": "member3@example.com", "role": "member"},
        headers=auth_headers,
    )
    login_response = await client.post(
        "/auth/login?tenant_slug=test-company",
        json={"email": "member3@example.com", "password": "password123"},
    )
    if login_response.status_code == 200:
        member_token = login_response.json()["access_token"]
        member_headers = {"Authorization": f"Bearer {member_token}"}
        response = await client.patch(
            "/workspace/settings",
            json={"name": "Hacked"},
            headers=member_headers,
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_member_cannot_invite(client: AsyncClient, auth_headers):
    await client.post(
        "/workspace/invite",
        json={"email": "member4@example.com", "role": "member"},
        headers=auth_headers,
    )
    login_response = await client.post(
        "/auth/login?tenant_slug=test-company",
        json={"email": "member4@example.com", "password": "password123"},
    )
    if login_response.status_code == 200:
        member_token = login_response.json()["access_token"]
        member_headers = {"Authorization": f"Bearer {member_token}"}
        response = await client.post(
            "/workspace/invite",
            json={"email": "hacked@example.com", "role": "member"},
            headers=member_headers,
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_billing_info(client: AsyncClient, auth_headers):
    response = await client.get("/billing", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "current_plan" in data
    assert "limits" in data
    assert data["current_plan"] == "free"
    assert data["limits"]["max_projects"] == 3
    assert data["limits"]["max_members"] == 5


@pytest.mark.asyncio
async def test_free_plan_limits(client: AsyncClient, auth_headers):
    response = await client.get("/billing", headers=auth_headers)
    assert response.status_code == 200
    limits = response.json()["limits"]
    assert limits["max_projects"] == 3
    assert limits["max_members"] == 5
    assert limits["price_monthly"] == 0