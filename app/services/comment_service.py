# app/services/comment_service.py

import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.db.mongodb import get_mongodb
from app.schemas.comment import CommentCreate, CommentResponse
from app.models.user import User


class CommentService:

    async def create_comment(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user: User,
        data: CommentCreate,
    ) -> CommentResponse:
        db = await get_mongodb()
        comment = {
            "task_id": str(task_id),
            "tenant_id": str(tenant_id),
            "user_id": str(user.id),
            "user_name": user.name,
            "body": data.body,
            "created_at": datetime.now(timezone.utc),
        }
        result = await db.comments.insert_one(comment)
        comment["id"] = str(result.inserted_id)
        return CommentResponse(**comment)

    async def get_comments(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> list[CommentResponse]:
        db = await get_mongodb()
        cursor = db.comments.find(
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
        db = await get_mongodb()
        result = await db.comments.delete_one({
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
