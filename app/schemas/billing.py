from pydantic import BaseModel
from app.models.tenant import PlanType


class CreateOrderRequest(BaseModel):
    plan: PlanType


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan: PlanType


class PlanLimits(BaseModel):
    max_projects: int
    max_members: int
    price_monthly: int


class BillingResponse(BaseModel):
    current_plan: PlanType
    limits: PlanLimits
    razorpay_key_id: str