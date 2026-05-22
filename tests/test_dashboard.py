import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_unauthenticated(client: AsyncClient):
    response = await client.get("/dashboard")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_dashboard_empty(client: AsyncClient, auth_headers):
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "projects" in data
    assert "recent_activity" in data
    assert "is_admin" in data
    assert data["is_admin"] == True
    assert isinstance(data["projects"], list)
    assert isinstance(data["recent_activity"], list)


@pytest.mark.asyncio
async def test_dashboard_admin_summary_fields(client: AsyncClient, auth_headers):
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert "total_members" in summary
    assert "total_projects" in summary
    assert "total_tasks" in summary
    assert "total_overdue" in summary


@pytest.mark.asyncio
async def test_dashboard_summary_counts_zero_initially(client: AsyncClient, auth_headers):
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert summary["total_tasks"] == 0
    assert summary["total_overdue"] == 0


@pytest.mark.asyncio
async def test_dashboard_shows_created_project(client: AsyncClient, auth_headers):
    await client.post(
        "/projects",
        json={"name": "Dashboard Test Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    projects = response.json()["projects"]
    assert len(projects) == 1
    assert projects[0]["name"] == "Dashboard Test Project"
    assert projects[0]["color"] == "#6366f1"


@pytest.mark.asyncio
async def test_dashboard_project_card_has_required_fields(client: AsyncClient, auth_headers):
    await client.post(
        "/projects",
        json={"name": "Card Fields Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    project = response.json()["projects"][0]
    assert "id" in project
    assert "name" in project
    assert "color" in project
    assert "total_tasks" in project
    assert "completed_tasks" in project
    assert "overdue_tasks" in project


@pytest.mark.asyncio
async def test_dashboard_total_tasks_updates_after_task_created(client: AsyncClient, auth_headers):
    project = await client.post(
        "/projects",
        json={"name": "Task Count Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = project.json()["id"]

    column = await client.post(
        f"/projects/{project_id}/columns",
        json={"name": "To Do", "position": 0},
        headers=auth_headers,
    )
    column_id = column.json()["id"]

    await client.post(
        f"/projects/{project_id}/columns/{column_id}/tasks",
        json={"title": "Task 1", "priority": "medium", "position": 0},
        headers=auth_headers,
    )

    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    project_card = response.json()["projects"][0]
    assert project_card["total_tasks"] == 1


@pytest.mark.asyncio
async def test_dashboard_multiple_projects(client: AsyncClient, auth_headers):
    for i in range(3):
        await client.post(
            "/projects",
            json={"name": f"Project {i+1}", "color": "#6366f1"},
            headers=auth_headers,
        )
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["projects"]) == 3


@pytest.mark.asyncio
async def test_dashboard_total_projects_in_summary(client: AsyncClient, auth_headers):
    await client.post(
        "/projects",
        json={"name": "Summary Count Project", "color": "#6366f1"},
        headers=auth_headers,
    )
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["summary"]["total_projects"] == 1


@pytest.mark.asyncio
async def test_dashboard_archived_project_not_shown(client: AsyncClient, auth_headers):
    project = await client.post(
        "/projects",
        json={"name": "Archive Me", "color": "#6366f1"},
        headers=auth_headers,
    )
    project_id = project.json()["id"]
    await client.delete(f"/projects/{project_id}", headers=auth_headers)

    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    ids = [p["id"] for p in response.json()["projects"]]
    assert project_id not in ids


@pytest.mark.asyncio
async def test_dashboard_recent_activity_is_list(client: AsyncClient, auth_headers):
    response = await client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["recent_activity"], list)