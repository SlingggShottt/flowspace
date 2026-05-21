import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse


class NotificationService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        type: str,
        title: str,
        body: str | None = None,
        task_id: uuid.UUID | None = None,
        project_id: uuid.UUID | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            tenant_id=tenant_id,
            type=type,
            title=title,
            body=body,
            task_id=task_id,
            project_id=project_id,
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def get_notifications(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        limit: int = 20,
    ) -> list[NotificationResponse]:
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.tenant_id == tenant_id,
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        notifications = result.scalars().all()
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def get_unread_count(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> int:
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.tenant_id == tenant_id,
                Notification.is_read == False,
            )
        )
        return len(result.scalars().all())

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        await self.db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True)
        )
        await self.db.flush()
        return {"message": "Marked as read"}

    async def mark_all_as_read(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> dict:
        await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.tenant_id == tenant_id,
                Notification.is_read == False,
            )
            .values(is_read=True)
        )
        await self.db.flush()
        return {"message": "All notifications marked as read"}