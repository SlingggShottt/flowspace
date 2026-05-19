import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.project import Project


class ProjectRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        name: str,
        description: str | None = None,
        color: str = "#6366f1",
        team_id: uuid.UUID | None = None,
    ) -> Project:
        project = Project(
            tenant_id=tenant_id,
            created_by=created_by,
            name=name,
            description=description,
            color=color,
            team_id=team_id,
        )
        self.db.add(project)
        await self.db.flush()
        return project

    async def get_by_id(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> Project | None:
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.tenant_id == tenant_id,
                Project.archived_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, tenant_id: uuid.UUID, team_ids: list[uuid.UUID] | None = None) -> list[Project]:
        query = select(Project).where(
            Project.tenant_id == tenant_id,
            Project.archived_at.is_(None),
        )
        if team_ids is not None:
            query = query.where(
                or_(Project.team_id.in_(team_ids), Project.team_id.is_(None))
            )
        query = query.order_by(Project.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            if value is not None:
                setattr(project, key, value)
        await self.db.flush()
        return project

    async def soft_delete(self, project: Project) -> Project:
        project.archived_at = datetime.now(timezone.utc)
        await self.db.flush()
        return project