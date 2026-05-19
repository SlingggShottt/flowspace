import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.membership import Membership
from app.models.user import UserRole


class MembershipRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        role: UserRole,
        invited_by: uuid.UUID | None = None,
    ) -> Membership:
        membership = Membership(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
            joined_at=datetime.now(timezone.utc),
        )
        self.db.add(membership)
        await self.db.flush()
        return membership

    async def get_by_user_and_tenant(
        self, user_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Membership | None:
        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, membership_id: uuid.UUID) -> Membership | None:
        result = await self.db.execute(
            select(Membership)
            .options(selectinload(Membership.user))
            .where(Membership.id == membership_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_tenant(self, tenant_id: uuid.UUID) -> list[Membership]:
        result = await self.db.execute(
            select(Membership)
            .options(selectinload(Membership.user))
            .where(Membership.tenant_id == tenant_id)
        )
        return list(result.scalars().all())

    async def count_admins(self, tenant_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(Membership).where(
                Membership.tenant_id == tenant_id,
                Membership.role == UserRole.ADMIN,
            )
        )
        return len(result.scalars().all())

    async def update_role(self, membership: Membership, role: UserRole) -> Membership:
        membership.role = role
        await self.db.flush()
        return membership

    async def delete(self, membership: Membership) -> None:
        await self.db.delete(membership)
        await self.db.flush()