import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.column_service import ColumnService
from app.schemas.column import ColumnCreate, ColumnUpdate

router = APIRouter(prefix="/projects/{project_id}/columns", tags=["Columns"])


@router.post("")
async def create_column(
    project_id: uuid.UUID,
    data: ColumnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ColumnService(db)
    return await service.create_column(project_id, current_user.tenant_id, data)


@router.get("")
async def list_columns(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ColumnService(db)
    return await service.list_columns(project_id, current_user.tenant_id)


@router.patch("/{column_id}")
async def update_column(
    project_id: uuid.UUID,
    column_id: uuid.UUID,
    data: ColumnUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ColumnService(db)
    return await service.update_column(column_id, current_user.tenant_id, data)


@router.delete("/{column_id}")
async def delete_column(
    project_id: uuid.UUID,
    column_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ColumnService(db)
    return await service.delete_column(column_id, current_user.tenant_id)