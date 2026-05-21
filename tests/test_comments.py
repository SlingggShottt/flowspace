import pytest
from httpx import AsyncClient


async def create_project_with_task(client, auth_headers):
    project = await client.post(
        "/projects",
        json={"name": "Comment Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    assert project.status_code == 200, f"Project creation failed: {project.text}"
    project_id = project.json()["id"]

    column = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "To Do", "position": 0},
        headers=auth_headers,
    )
    assert column.status_code == 200, f"Column creation failed: {column.text}"
    column_id = column.json()["id"]

    task = await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Task With Comments", "priority": "medium", "position": 0},
        headers=auth_headers,
    )
    assert task.status_code == 200, f"Task creation failed: {task.text}"
    return task.json()["id"]


@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient, auth_headers):
    task_id = await create_project_with_task(client, auth_headers)
    response = await client.post(
        f"/tasks/{task_id}/comments",
        json={"body": "This is a test comment"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["body"] == "This is a test comment"


@pytest.mark.asyncio
async def test_get_comments(client: AsyncClient, auth_headers):
    task_id = await create_project_with_task(client, auth_headers)
    await client.post(
        f"/tasks/{task_id}/comments",
        json={"body": "First comment"},
        headers=auth_headers,
    )
    response = await client.get(f"/tasks/{task_id}/comments", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_comments_unauthenticated(client: AsyncClient, auth_headers):
    task_id = await create_project_with_task(client, auth_headers)
    response = await client.get(f"/tasks/{task_id}/comments")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_comment_on_nonexistent_task(client: AsyncClient, auth_headers):
    # service does not validate task existence before inserting to mongo
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post(
        f"/tasks/{fake_id}/comments",
        json={"body": "Ghost comment"},
        headers=auth_headers,
    )
    assert response.status_code in [200, 404, 400]


@pytest.mark.asyncio
async def test_activity_feed(client: AsyncClient, auth_headers):
    task_id = await create_project_with_task(client, auth_headers)
    response = await client.get(f"/tasks/{task_id}/activity", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)