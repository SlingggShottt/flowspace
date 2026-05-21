import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_notifications_empty(client: AsyncClient, auth_headers):
    response = await client.get("/notifications", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_notifications_unauthenticated(client: AsyncClient):
    response = await client.get("/notifications")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_get_unread_count(client: AsyncClient, auth_headers):
    response = await client.get("/notifications/unread-count", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] == 0


@pytest.mark.asyncio
async def test_get_unread_count_unauthenticated(client: AsyncClient):
    response = await client.get("/notifications/unread-count")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_mark_all_as_read(client: AsyncClient, auth_headers):
    response = await client.patch("/notifications/mark-all-read", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_mark_all_as_read_unauthenticated(client: AsyncClient):
    response = await client.patch("/notifications/mark-all-read")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_mark_nonexistent_notification_as_read(client: AsyncClient, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(f"/notifications/{fake_id}/read", headers=auth_headers)
    assert response.status_code in [404, 200]


@pytest.mark.asyncio
async def test_unread_count_after_mark_all_read(client: AsyncClient, auth_headers):
    await client.patch("/notifications/mark-all-read", headers=auth_headers)
    response = await client.get("/notifications/unread-count", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["count"] == 0
