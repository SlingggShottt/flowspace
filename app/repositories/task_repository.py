import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task, PriorityType


class TaskRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: uuid.UUID,
        project_id: uuid.UUID,
        column_id: uuid.UUID,
        title: str,
        description: str | None = None,
        assignee_id: uuid.UUID | None = None,
        priority: PriorityType = PriorityType.MEDIUM,
        due_date: datetime | None = None,
        position: int = 0,
    ) -> Task:
        task = Task(
            tenant_id=tenant_id,
            project_id=project_id,
            column_id=column_id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            priority=priority,
            due_date=due_date,
            position=position,
        )
        self.db.add(task)
        await self.db.flush()
        return task

    async def get_by_id(self, task_id: uuid.UUID, tenant_id: uuid.UUID) -> Task | None:
        result = await self.db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.tenant_id == tenant_id,
                Task.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_column(self, column_id: uuid.UUID, tenant_id: uuid.UUID) -> list[Task]:
        result = await self.db.execute(
            select(Task).where(
                Task.column_id == column_id,
                Task.tenant_id == tenant_id,
                Task.deleted_at.is_(None),
            ).order_by(Task.position.asc())
        )
        return list(result.scalars().all())

    async def get_by_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> list[Task]:
        result = await self.db.execute(
            select(Task).where(
                Task.project_id == project_id,
                Task.tenant_id == tenant_id,
                Task.deleted_at.is_(None),
            ).order_by(Task.position.asc())
        )
        return list(result.scalars().all())

    async def update(self, task: Task, **kwargs) -> Task:
        for key, value in kwargs.items():
            setattr(task, key, value)
        await self.db.flush()
        return task

    async def move(self, task: Task, column_id: uuid.UUID, position: int) -> Task:
        task.column_id = column_id
        task.position = position
        await self.db.flush()
        return task

    async def soft_delete(self, task: Task) -> Task:
        task.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()
        return task

    async def search(self, tenant_id: uuid.UUID, query: str) -> list[Task]:
        result = await self.db.execute(
            select(Task).where(
                Task.tenant_id == tenant_id,
                Task.deleted_at.is_(None),
                Task.title.ilike(f"%{query}%"),
            )
        )
        return list(result.scalars().all())