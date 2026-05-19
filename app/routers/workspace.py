import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.services.workspace_service import WorkspaceService
from app.services.membership_service import MembershipService
from app.schemas.workspace import WorkspaceUpdate
from app.schemas.membership import MemberRoleUpdate, InviteRequest

router = APIRouter(prefix="/workspace", tags=["Workspace"])


@router.get("/settings")
async def get_workspace(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkspaceService(db)
    return await service.get_workspace(current_user.tenant_id)


@router.patch("/settings")
async def update_workspace(
    data: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = WorkspaceService(db)
    return await service.update_workspace(current_user.tenant_id, data)


@router.get("/members")
async def list_members(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MembershipService(db)
    return await service.list_members(current_user.tenant_id)


@router.post("/invite")
async def invite_member(
    data: InviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = MembershipService(db)
    return await service.invite_member(data, current_user.tenant_id, current_user.id)


@router.patch("/members/{membership_id}/role")
async def update_member_role(
    membership_id: uuid.UUID,
    data: MemberRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = MembershipService(db)
    return await service.update_member_role(
        membership_id, current_user.tenant_id, current_user.id, data
    )


@router.delete("/members/{membership_id}")
async def remove_member(
    membership_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = MembershipService(db)
    return await service.remove_member(
        membership_id, current_user.tenant_id, current_user.id
    )