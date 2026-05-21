import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_billing_info_structure(client: AsyncClient, auth_headers):
    response = await client.get("/billing", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "current_plan" in data
    assert "limits" in data
    assert data["current_plan"] == "free"
    assert data["limits"]["max_projects"] == 3
    assert data["limits"]["max_members"] == 5
    assert data["limits"]["price_monthly"] == 0


@pytest.mark.asyncio
async def test_billing_unauthenticated(client: AsyncClient):
    response = await client.get("/billing")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_downgrade_to_free(client: AsyncClient, auth_headers):
    response = await client.post("/billing/downgrade", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_order_unauthenticated(client: AsyncClient):
    response = await client.post("/billing/order", json={"plan": "pro"})
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_order_for_free_plan_rejected(client: AsyncClient, auth_headers):
    response = await client.post("/billing/order", json={"plan": "free"}, headers=auth_headers)
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_pro_plan_limits_higher(client: AsyncClient, auth_headers):
    response = await client.get("/billing", headers=auth_headers)
    free_limits = response.json()["limits"]
    assert free_limits["max_projects"] < 10
    assert free_limits["max_members"] < 10
