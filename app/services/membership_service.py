import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.membership_repository import MembershipRepository
from app.repositories.user_repository import UserRepository
from app.repositories.tenant_repository import TenantRepository
from app.models.user import UserRole
from app.schemas.membership import MemberResponse, MemberRoleUpdate, InviteRequest
from app.schemas.user import UserResponse
from app.core.security import hash_password
import secrets


class MembershipService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.membership_repo = MembershipRepository(db)
        self.user_repo = UserRepository(db)
        self.tenant_repo = TenantRepository(db)

    async def list_members(self, tenant_id: uuid.UUID) -> list[MemberResponse]:
        memberships = await self.membership_repo.get_all_by_tenant(tenant_id)
        return [MemberResponse.model_validate(m) for m in memberships]

    async def invite_member(
        self,
        data: InviteRequest,
        tenant_id: uuid.UUID,
        invited_by: uuid.UUID,
    ) -> dict:
        existing = await self.user_repo.get_by_email_and_tenant(data.email, tenant_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists in this workspace",
            )

        temp_password = secrets.token_urlsafe(16)
        password_hash = hash_password(temp_password)

        user = await self.user_repo.create(
            tenant_id=tenant_id,
            email=data.email,
            name=data.email.split("@")[0],
            password_hash=password_hash,
            role=data.role,
        )

        await self.membership_repo.create(
            tenant_id=tenant_id,
            user_id=user.id,
            role=data.role,
            invited_by=invited_by,
        )

        return {
            "message": f"User {data.email} invited successfully",
            "temp_password": temp_password,
            "user": UserResponse.model_validate(user),
        }

    async def update_member_role(
        self,
        membership_id: uuid.UUID,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID,
        data: MemberRoleUpdate,
    ) -> MemberResponse:
        membership = await self.membership_repo.get_by_id(membership_id)
        if not membership or membership.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        if membership.user_id == current_user_id and data.role != UserRole.ADMIN:
            admin_count = await self.membership_repo.count_admins(tenant_id)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove admin role from the only admin",
                )

        updated = await self.membership_repo.update_role(membership, data.role)
        return MemberResponse.model_validate(updated)

    async def remove_member(
        self,
        membership_id: uuid.UUID,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> dict:
        membership = await self.membership_repo.get_by_id(membership_id)
        if not membership or membership.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        if membership.user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself from the workspace",
            )

        if membership.role == UserRole.ADMIN:
            admin_count = await self.membership_repo.count_admins(tenant_id)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the only admin from the workspace",
                )

        await self.membership_repo.delete(membership)
        return {"message": "Member removed successfully"}