import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.repositories.column_repository import ColumnRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskMove, TaskResponse


class TaskService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TaskRepository(db)
        self.column_repo = ColumnRepository(db)

    async def create_task(
        self, column_id: uuid.UUID, tenant_id: uuid.UUID, project_id: uuid.UUID, data: TaskCreate
    ) -> TaskResponse:
        column = await self.column_repo.get_by_id(column_id, tenant_id)
        if not column:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
        task = await self.repo.create(
            tenant_id=tenant_id,
            project_id=project_id,
            column_id=column_id,
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
            priority=data.priority,
            due_date=data.due_date,
            position=data.position,
        )
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: uuid.UUID, tenant_id: uuid.UUID) -> TaskResponse:
        task = await self.repo.get_by_id(task_id, tenant_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return TaskResponse.model_validate(task)

    async def list_tasks_by_project(
        self, project_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[TaskResponse]:
        tasks = await self.repo.get_by_project(project_id, tenant_id)
        return [TaskResponse.model_validate(t) for t in tasks]

    async def update_task(
        self, task_id: uuid.UUID, tenant_id: uuid.UUID, data: TaskUpdate
    ) -> TaskResponse:
        task = await self.repo.get_by_id(task_id, tenant_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        updated = await self.repo.update(task, **data.model_dump(exclude_none=True))
        return TaskResponse.model_validate(updated)

    async def move_task(
        self, task_id: uuid.UUID, tenant_id: uuid.UUID, data: TaskMove
    ) -> TaskResponse:
        task = await self.repo.get_by_id(task_id, tenant_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        column = await self.column_repo.get_by_id(data.column_id, tenant_id)
        if not column:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
        moved = await self.repo.move(task, data.column_id, data.position)
        return TaskResponse.model_validate(moved)

    async def delete_task(self, task_id: uuid.UUID, tenant_id: uuid.UUID) -> dict:
        task = await self.repo.get_by_id(task_id, tenant_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        await self.repo.soft_delete(task)
        return {"message": "Task deleted successfully"}

    async def search_tasks(self, tenant_id: uuid.UUID, query: str) -> list[TaskResponse]:
        tasks = await self.repo.search(tenant_id, query)
        return [TaskResponse.model_validate(t) for t in tasks]