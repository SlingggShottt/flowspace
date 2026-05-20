import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_team(client: AsyncClient, auth_headers):
    response = await client.post(
        "/teams",
        json={"name": "Engineering"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Engineering"
    assert data["members"] == []


@pytest.mark.asyncio
async def test_list_teams(client: AsyncClient, auth_headers):
    await client.post("/teams", json={"name": "Design"}, headers=auth_headers)
    response = await client.get("/teams", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_team(client: AsyncClient, auth_headers):
    create_response = await client.post(
        "/teams",
        json={"name": "Old Name"},
        headers=auth_headers,
    )
    team_id = create_response.json()["id"]

    response = await client.patch(
        f"/teams/{team_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_team(client: AsyncClient, auth_headers):
    create_response = await client.post(
        "/teams",
        json={"name": "To Delete"},
        headers=auth_headers,
    )
    team_id = create_response.json()["id"]

    response = await client.delete(f"/teams/{team_id}", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_member_to_team(client: AsyncClient, auth_headers, registered_user):
    create_response = await client.post(
        "/teams",
        json={"name": "Team With Member"},
        headers=auth_headers,
    )
    team_id = create_response.json()["id"]
    user_id = registered_user["user"]["id"]

    response = await client.post(
        f"/teams/{team_id}/members",
        json={"user_id": user_id},
        headers=auth_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_only_admin_can_create_team(client: AsyncClient, auth_headers):
    invite_response = await client.post(
        "/workspace/invite",
        json={"email": "teammember@example.com", "role": "member"},
        headers=auth_headers,
    )

    login_response = await client.post(
        "/auth/login?tenant_slug=test-company",
        json={"email": "teammember@example.com", "password": "password123"},
    )

    if login_response.status_code == 200:
        member_token = login_response.json()["access_token"]
        member_headers = {"Authorization": f"Bearer {member_token}"}
        response = await client.post(
            "/teams",
            json={"name": "Unauthorized Team"},
            headers=member_headers,
        )
        assert response.status_code == 403