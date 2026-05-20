import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers):
    response = await client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "A test project",
            "color": "#6366f1",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["color"] == "#6366f1"
    return data


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, auth_headers):
    response = await client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, auth_headers):
    create_response = await client.post(
        "/projects",
        json={"name": "Get Test Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == project_id


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, auth_headers):
    create_response = await client.post(
        "/projects",
        json={"name": "Update Test Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.patch(
        f"/projects/{project_id}",
        json={"name": "Updated Project Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project Name"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, auth_headers):
    create_response = await client.post(
        "/projects",
        json={"name": "Delete Test Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200

    get_response = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_column(client: AsyncClient, auth_headers):
    create_response = await client.post(
        "/projects",
        json={"name": "Column Test Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "To Do", "position": 0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "To Do"