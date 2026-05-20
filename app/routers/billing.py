from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.services.billing_service import BillingService
from app.schemas.billing import CreateOrderRequest, VerifyPaymentRequest

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("")
async def get_billing_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BillingService(db)
    return await service.get_billing_info(current_user.tenant_id)


@router.post("/order")
async def create_order(
    data: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = BillingService(db)
    return await service.create_order(current_user.tenant_id, data)


@router.post("/verify")
async def verify_payment(
    data: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = BillingService(db)
    return await service.verify_payment(current_user.tenant_id, data)


@router.post("/downgrade")
async def downgrade_to_free(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = BillingService(db)
    return await service.downgrade_to_free(current_user.tenant_id)