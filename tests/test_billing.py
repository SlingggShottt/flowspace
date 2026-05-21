import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_billing_info(client: AsyncClient, auth_headers):
    response = await client.get("/billing", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "current_plan" in data
    assert "limits" in data
    assert "razorpay_key_id" in data


@pytest.mark.asyncio
async def test_default_plan_is_free(client: AsyncClient, auth_headers):
    response = await client.get("/billing", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["current_plan"] == "free"


@pytest.mark.asyncio
async def test_free_plan_limits(client: AsyncClient, auth_headers):
    response = await client.get("/billing", headers=auth_headers)
    limits = response.json()["limits"]
    assert limits["max_projects"] == 3
    assert limits["max_members"] == 5
    assert limits["price_monthly"] == 0


@pytest.mark.asyncio
async def test_create_order_for_free_plan_fails(client: AsyncClient, auth_headers):
    response = await client.post(
        "/billing/order",
        json={"plan": "free"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_order_for_pro_plan(client: AsyncClient, auth_headers):
    response = await client.post(
        "/billing/order",
        json={"plan": "pro"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "order_id" in data
    assert "amount" in data
    assert data["amount"] == 99900


@pytest.mark.asyncio
async def test_create_order_for_enterprise_plan(client: AsyncClient, auth_headers):
    response = await client.post(
        "/billing/order",
        json={"plan": "enterprise"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 299900


@pytest.mark.asyncio
async def test_downgrade_to_free(client: AsyncClient, auth_headers):
    response = await client.post("/billing/downgrade", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Plan downgraded to free"


@pytest.mark.asyncio
async def test_member_cannot_create_order(client: AsyncClient, auth_headers):
    await client.post(
        "/workspace/invite",
        json={"email": "billingmember@example.com", "role": "member"},
        headers=auth_headers,
    )
    login_response = await client.post(
        "/auth/login?tenant_slug=test-company",
        json={"email": "billingmember@example.com", "password": "password123"},
    )
    if login_response.status_code == 200:
        member_token = login_response.json()["access_token"]
        member_headers = {"Authorization": f"Bearer {member_token}"}
        response = await client.post(
            "/billing/order",
            json={"plan": "pro"},
            headers=member_headers,
        )
        assert response.status_code == 403