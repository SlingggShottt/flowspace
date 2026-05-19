import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class MemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: UserRole
    joined_at: datetime | None = None

    model_config = {"from_attributes": True}


class MemberRoleUpdate(BaseModel):
    role: UserRole


class InviteRequest(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER