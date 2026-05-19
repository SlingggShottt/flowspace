import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.tenant_repository import TenantRepository
from app.schemas.workspace import WorkspaceResponse, WorkspaceUpdate


class WorkspaceService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tenant_repo = TenantRepository(db)

    async def get_workspace(self, tenant_id: uuid.UUID) -> WorkspaceResponse:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return WorkspaceResponse.model_validate(tenant)

    async def update_workspace(
        self, tenant_id: uuid.UUID, data: WorkspaceUpdate
    ) -> WorkspaceResponse:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        if data.name:
            tenant.name = data.name
        await self.db.flush()
        return WorkspaceResponse.model_validate(tenant)