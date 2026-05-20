import uuid
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserResponse, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.repositories.user_repository import UserRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.email_service import EmailService

router = APIRouter(prefix="/users", tags=["Users"])

# In-memory token store — in production use Redis
reset_tokens: dict = {}


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    avatar_url: str | None = None


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch("/me")
async def update_profile(
    data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.name:
        current_user.name = data.name
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    await db.flush()
    return UserResponse.model_validate(current_user)


@router.post("/me/change-password")
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters",
        )
    repo = UserRepository(db)
    await repo.update_password(current_user, hash_password(data.new_password))
    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    tenant_repo = TenantRepository(db)
    user_repo = UserRepository(db)

    tenant = await tenant_repo.get_by_slug(data.tenant_slug)
    if not tenant:
        return {"message": "If that email exists you will receive a reset link"}

    user = await user_repo.get_by_email_and_tenant(data.email, tenant.id)
    if not user:
        return {"message": "If that email exists you will receive a reset link"}

    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "user_id": str(user.id),
        "expires": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    email_service = EmailService()
    email_service.send_password_reset_email(
        to=user.email,
        name=user.name,
        reset_token=token,
    )

    return {"message": "If that email exists you will receive a reset link"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    token_data = reset_tokens.get(data.token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if datetime.now(timezone.utc) > token_data["expires"]:
        del reset_tokens[data.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(token_data["user_id"]))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await user_repo.update_password(user, hash_password(data.new_password))
    del reset_tokens[data.token]

    return {"message": "Password reset successfully"}