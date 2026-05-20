import uuid
import hmac
import hashlib
import razorpay
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repositories.tenant_repository import TenantRepository
from app.models.tenant import PlanType
from app.schemas.billing import BillingResponse, PlanLimits, CreateOrderRequest, VerifyPaymentRequest


PLAN_LIMITS = {
    PlanType.FREE: PlanLimits(max_projects=3, max_members=5, price_monthly=0),
    PlanType.PRO: PlanLimits(max_projects=999, max_members=999, price_monthly=999),
    PlanType.ENTERPRISE: PlanLimits(max_projects=999, max_members=999, price_monthly=2999),
}

PLAN_PRICES_PAISE = {
    PlanType.PRO: 99900,
    PlanType.ENTERPRISE: 299900,
}


class BillingService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tenant_repo = TenantRepository(db)
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    async def get_billing_info(self, tenant_id: uuid.UUID) -> BillingResponse:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
        return BillingResponse(
            current_plan=tenant.plan,
            limits=PLAN_LIMITS[tenant.plan],
            razorpay_key_id=settings.RAZORPAY_KEY_ID,
        )

    async def create_order(self, tenant_id: uuid.UUID, data: CreateOrderRequest) -> dict:
        if data.plan == PlanType.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create order for free plan",
            )

        amount = PLAN_PRICES_PAISE.get(data.plan)
        if not amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan",
            )

        order = self.client.order.create({
            "amount": amount,
            "currency": "INR",
            "notes": {
                "tenant_id": str(tenant_id),
                "plan": data.plan.value,
            }
        })

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "plan": data.plan,
        }

    async def verify_payment(self, tenant_id: uuid.UUID, data: VerifyPaymentRequest) -> dict:
        body = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if expected_signature != data.razorpay_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature",
            )

        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

        tenant.plan = data.plan
        await self.db.flush()

        return {"message": "Payment verified and plan upgraded", "plan": data.plan}

    async def downgrade_to_free(self, tenant_id: uuid.UUID) -> dict:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
        tenant.plan = PlanType.FREE
        await self.db.flush()
        return {"message": "Plan downgraded to free"}