import pytest
from httpx import AsyncClient


async def setup_project_and_column(client, auth_headers):
    project = await client.post(
        "/projects",
        json={"name": "Task Extra Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    assert project.status_code == 200
    project_id = project.json()["id"]

    column = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "To Do", "position": 0},
        headers=auth_headers,
    )
    assert column.status_code == 200
    return project_id, column.json()["id"]


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, auth_headers):
    project_id, column_id = await setup_project_and_column(client, auth_headers)
    task = await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Update Me", "priority": "low", "position": 0},
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "high"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["priority"] == "high"


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, auth_headers):
    project_id, column_id = await setup_project_and_column(client, auth_headers)
    task = await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Delete Me", "priority": "low", "position": 0},
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = await client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_deleted_task_not_in_search(client: AsyncClient, auth_headers):
    project_id, column_id = await setup_project_and_column(client, auth_headers)
    task = await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "GhostTask12345", "priority": "low", "position": 0},
        headers=auth_headers,
    )
    task_id = task.json()["id"]
    await client.delete(f"/tasks/{task_id}", headers=auth_headers)

    search = await client.get("/tasks/search?q=GhostTask12345", headers=auth_headers)
    assert search.status_code == 200
    ids = [t["id"] for t in search.json()]
    assert task_id not in ids


@pytest.mark.asyncio
async def test_task_priority_levels(client: AsyncClient, auth_headers):
    project_id, column_id = await setup_project_and_column(client, auth_headers)
    for priority in ["low", "medium", "high", "critical"]:
        task = await client.post(
            f"/projects/{project_id}/columns/{column_id}/tasks",
            json={"title": f"{priority} task", "priority": priority, "position": 0},
            headers=auth_headers,
        )
        assert task.status_code == 200
        assert task.json()["priority"] == priority


@pytest.mark.asyncio
async def test_update_task_unauthenticated(client: AsyncClient, auth_headers):
    project_id, column_id = await setup_project_and_column(client, auth_headers)
    task = await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Auth Test Task", "priority": "low", "position": 0},
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = await client.patch(f"/tasks/{task_id}", json={"title": "Hacked"})
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, auth_headers):
    project_id, column_id = await setup_project_and_column(client, auth_headers)
    task = await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Get Me", "priority": "medium", "position": 0},
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = await client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id


@pytest.mark.asyncio
async def test_list_tasks_in_project(client: AsyncClient, auth_headers):
    project_id, column_id = await setup_project_and_column(client, auth_headers)
    await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Listed Task", "priority": "low", "position": 0},
        headers=auth_headers,
    )
    response = await client.get(f"/projects/{project_id}/tasks", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1
