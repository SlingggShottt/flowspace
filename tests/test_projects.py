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


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers):
    project_response = await client.post(
        "/projects",
        json={"name": "Task Test Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = project_response.json()["id"]

    column_response = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "To Do", "position": 0},
        headers=auth_headers,
    )
    column_id = column_response.json()["id"]

    response = await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Test Task", "priority": "medium", "position": 0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


@pytest.mark.asyncio
async def test_move_task(client: AsyncClient, auth_headers):
    project_response = await client.post(
        "/projects",
        json={"name": "Move Task Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = project_response.json()["id"]

    col1_response = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "Col 1", "position": 0},
        headers=auth_headers,
    )
    col1_id = col1_response.json()["id"]

    col2_response = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "Col 2", "position": 1},
        headers=auth_headers,
    )
    col2_id = col2_response.json()["id"]

    task_response = await client.post(
        f"/projects/{project_id}/columns/{col1_id}/tasks",
        json={"title": "Move Me", "priority": "medium", "position": 0},
        headers=auth_headers,
    )
    task_id = task_response.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}/move",
        json={"column_id": col2_id, "position": 0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["column_id"] == col2_id


@pytest.mark.asyncio
async def test_search_tasks(client: AsyncClient, auth_headers):
    project_response = await client.post(
        "/projects",
        json={"name": "Search Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = project_response.json()["id"]

    col_response = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "To Do", "position": 0},
        headers=auth_headers,
    )
    col_id = col_response.json()["id"]

    await client.post(
        f"/projects/{project_id}/columns/{col_id}/tasks",
        json={"title": "Searchable Task", "priority": "medium", "position": 0},
        headers=auth_headers,
    )

    response = await client.get("/tasks/search?q=Searchable", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)