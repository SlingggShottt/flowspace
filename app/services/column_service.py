import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.column_repository import ColumnRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.column import ColumnCreate, ColumnUpdate, ColumnResponse


class ColumnService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ColumnRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create_column(
        self, project_id: uuid.UUID, tenant_id: uuid.UUID, data: ColumnCreate
    ) -> ColumnResponse:
        project = await self.project_repo.get_by_id(project_id, tenant_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        column = await self.repo.create(
            tenant_id=tenant_id,
            project_id=project_id,
            name=data.name,
            position=data.position,
        )
        return ColumnResponse.model_validate(column)

    async def list_columns(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> list[ColumnResponse]:
        columns = await self.repo.get_by_project(project_id, tenant_id)
        return [ColumnResponse.model_validate(c) for c in columns]

    async def update_column(
        self, column_id: uuid.UUID, tenant_id: uuid.UUID, data: ColumnUpdate
    ) -> ColumnResponse:
        column = await self.repo.get_by_id(column_id, tenant_id)
        if not column:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
        updated = await self.repo.update(column, **data.model_dump(exclude_none=True))
        return ColumnResponse.model_validate(updated)

    async def delete_column(self, column_id: uuid.UUID, tenant_id: uuid.UUID) -> dict:
        column = await self.repo.get_by_id(column_id, tenant_id)
        if not column:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
        await self.repo.delete(column)
        return {"message": "Column deleted successfully"}