from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.repositories.user_repository import UserRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.membership_repository import MembershipRepository
from app.models.user import UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.tenant_repo = TenantRepository(db)
        self.membership_repo = MembershipRepository(db)

    async def register(self, data: RegisterRequest) -> dict:
        tenant = await self.tenant_repo.create(name=data.company_name)

        existing = await self.user_repo.get_by_email_and_tenant(data.email, tenant.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered for this workspace",
            )

        password_hash = hash_password(data.password)
        user = await self.user_repo.create(
            tenant_id=tenant.id,
            email=data.email,
            name=data.name,
            password_hash=password_hash,
            role=UserRole.ADMIN,
        )

        await self.membership_repo.create(
            tenant_id=tenant.id,
            user_id=user.id,
            role=UserRole.ADMIN,
        )

        token_data = {"sub": str(user.id), "tenant_id": str(tenant.id), "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }

    async def login(self, data: LoginRequest, tenant_slug: str) -> dict:
        tenant = await self.tenant_repo.get_by_slug(tenant_slug)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        user = await self.user_repo.get_by_email_and_tenant(data.email, tenant.id)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token_data = {"sub": str(user.id), "tenant_id": str(tenant.id), "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }

    async def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user = await self.user_repo.get_by_id(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        token_data = {"sub": str(user.id), "tenant_id": payload["tenant_id"], "role": user.role}
        access_token = create_access_token(token_data)

        return {"access_token": access_token, "token_type": "bearer"}