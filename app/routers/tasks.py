import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskMove

router = APIRouter(tags=["Tasks"])


@router.post("/projects/{project_id}/columns/{column_id}/tasks")
async def create_task(
    project_id: uuid.UUID,
    column_id: uuid.UUID,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return await service.create_task(
        column_id, current_user.tenant_id, project_id, data,
        current_user.id, current_user.name
    )


@router.get("/projects/{project_id}/tasks")
async def list_tasks(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return await service.list_tasks_by_project(project_id, current_user.tenant_id)


@router.get("/tasks/search")
async def search_tasks(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return await service.search_tasks(current_user.tenant_id, q)


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return await service.get_task(task_id, current_user.tenant_id)


@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return await service.update_task(
        task_id, current_user.tenant_id, data,
        current_user.id, current_user.name
    )


@router.patch("/tasks/{task_id}/move")
async def move_task(
    task_id: uuid.UUID,
    data: TaskMove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return await service.move_task(
        task_id, current_user.tenant_id, data,
        current_user.id, current_user.name
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return await service.delete_task(task_id, current_user.tenant_id)