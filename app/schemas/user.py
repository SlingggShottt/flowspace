import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    role: UserRole
    avatar_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}