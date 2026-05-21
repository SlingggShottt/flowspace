import pytest
from httpx import AsyncClient


async def create_project(client, auth_headers):
    response = await client.post(
        "/projects",
        json={"name": "Column Test Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_multiple_columns(client: AsyncClient, auth_headers):
    project_id = await create_project(client, auth_headers)
    for i, name in enumerate(["To Do", "In Progress", "Done"]):
        response = await client.post(
            f"/projects/{project_id}/columns",
            json={"name": name, "position": i},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == name


@pytest.mark.asyncio
async def test_list_columns(client: AsyncClient, auth_headers):
    project_id = await create_project(client, auth_headers)
    await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "To Do", "position": 0},
        headers=auth_headers,
    )
    response = await client.get(f"/projects/{project_id}/columns", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_rename_column(client: AsyncClient, auth_headers):
    project_id = await create_project(client, auth_headers)
    col = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "Old Name", "position": 0},
        headers=auth_headers,
    )
    column_id = col.json()["id"]

    # correct route: /projects/{project_id}/columns/{column_id}
    response = await client.patch(
        f"/projects/{project_id}/columns/{column_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_column(client: AsyncClient, auth_headers):
    project_id = await create_project(client, auth_headers)
    col = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "Delete Me", "position": 0},
        headers=auth_headers,
    )
    column_id = col.json()["id"]

    response = await client.delete(
        f"/projects/{project_id}/columns/{column_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_column_unauthenticated(client: AsyncClient, auth_headers):
    project_id = await create_project(client, auth_headers)
    response = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "Hacked Column", "position": 0},
    )
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_column_belongs_to_project(client: AsyncClient, auth_headers):
    project_id = await create_project(client, auth_headers)
    col = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "Scoped Column", "position": 0},
        headers=auth_headers,
    )
    assert col.json()["project_id"] == project_id
