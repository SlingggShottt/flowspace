import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.mongodb import get_mongodb
from app.schemas.comment import CommentCreate, CommentResponse
from app.models.user import User
from app.models.task import Task
from app.models.project import Project


class CommentService:

    async def create_comment(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user: User,
        data: CommentCreate,
        db: AsyncSession,
    ) -> CommentResponse:
        mongo = await get_mongodb()
        comment = {
            "task_id": str(task_id),
            "tenant_id": str(tenant_id),
            "user_id": str(user.id),
            "user_name": user.name,
            "body": data.body,
            "created_at": datetime.now(timezone.utc),
        }
        result = await mongo.comments.insert_one(comment)
        comment["id"] = str(result.inserted_id)

        await self._notify_assignee(task_id, tenant_id, user, data.body, db)

        return CommentResponse(**comment)

    async def _notify_assignee(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        commenter: User,
        comment_body: str,
        db: AsyncSession,
    ) -> None:
        try:
            from app.services.email_service import EmailService
            task_result = await db.execute(select(Task).where(Task.id == task_id))
            task = task_result.scalar_one_or_none()
            if not task or not task.assignee_id or task.assignee_id == commenter.id:
                return

            assignee_result = await db.execute(select(User).where(User.id == task.assignee_id))
            assignee = assignee_result.scalar_one_or_none()
            if not assignee:
                return

            project_result = await db.execute(select(Project).where(Project.id == task.project_id))
            project = project_result.scalar_one_or_none()

            email_service = EmailService()
            email_service.send_comment_notification_email(
                to=assignee.email,
                recipient_name=assignee.name,
                commenter_name=commenter.name,
                task_title=task.title,
                comment_body=comment_body[:200],
                project_name=project.name if project else "Flowspace",
            )
        except Exception as e:
            print(f"Comment notification error: {e}")

    async def get_comments(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> list[CommentResponse]:
        mongo = await get_mongodb()
        cursor = mongo.comments.find(
            {"task_id": str(task_id), "tenant_id": str(tenant_id)}
        ).sort("created_at", 1)
        comments = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            comments.append(CommentResponse(**doc))
        return comments

    async def delete_comment(
        self,
        comment_id: str,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        from bson import ObjectId
        mongo = await get_mongodb()
        result = await mongo.comments.delete_one({
            "_id": ObjectId(comment_id),
            "tenant_id": str(tenant_id),
            "user_id": str(user_id),
        })
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        return {"message": "Comment deleted"}