import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
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