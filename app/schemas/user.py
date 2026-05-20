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
    must_change_password: bool = False

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    tenant_slug: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str