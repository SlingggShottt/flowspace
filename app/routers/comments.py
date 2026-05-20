import uuid
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.comment_service import CommentService
from app.services.activity_service import ActivityService
from app.schemas.comment import CommentCreate

router = APIRouter(tags=["Comments"])


@router.post("/tasks/{task_id}/comments")
async def create_comment(
    task_id: uuid.UUID,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
):
    service = CommentService()
    activity = ActivityService()
    comment = await service.create_comment(task_id, current_user.tenant_id, current_user, data)
    await activity.log_activity(
        task_id=task_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_name=current_user.name,
        action="commented",
        detail=data.body[:100],
    )
    return comment


@router.get("/tasks/{task_id}/comments")
async def get_comments(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    service = CommentService()
    return await service.get_comments(task_id, current_user.tenant_id)


@router.delete("/tasks/{task_id}/comments/{comment_id}")
async def delete_comment(
    task_id: uuid.UUID,
    comment_id: str,
    current_user: User = Depends(get_current_user),
):
    service = CommentService()
    return await service.delete_comment(comment_id, current_user.tenant_id, current_user.id)


@router.get("/tasks/{task_id}/activity")
async def get_activity(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    service = ActivityService()
    return await service.get_activity(task_id, current_user.tenant_id)