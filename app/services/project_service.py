import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProjectRepository(db)

    async def create_project(
        self, data: ProjectCreate, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectResponse:
        project = await self.repo.create(
            tenant_id=tenant_id,
            created_by=user_id,
            name=data.name,
            description=data.description,
            color=data.color,
        )
        return ProjectResponse.model_validate(project)

    async def get_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id, tenant_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return ProjectResponse.model_validate(project)

    async def list_projects(self, tenant_id: uuid.UUID) -> list[ProjectResponse]:
        projects = await self.repo.get_all(tenant_id)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def update_project(
        self, project_id: uuid.UUID, tenant_id: uuid.UUID, data: ProjectUpdate
    ) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id, tenant_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        updated = await self.repo.update(project, **data.model_dump(exclude_none=True))
        return ProjectResponse.model_validate(updated)

    async def delete_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> dict:
        project = await self.repo.get_by_id(project_id, tenant_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        await self.repo.soft_delete(project)
        return {"message": "Project archived successfully"}