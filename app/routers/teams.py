import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.services.team_service import TeamService
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberAdd

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("")
async def create_team(
    data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = TeamService(db)
    return await service.create_team(data, current_user.tenant_id, current_user.id)


@router.get("")
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TeamService(db)
    return await service.list_teams(current_user.tenant_id)


@router.patch("/{team_id}")
async def update_team(
    team_id: uuid.UUID,
    data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = TeamService(db)
    return await service.update_team(team_id, current_user.tenant_id, data)


@router.delete("/{team_id}")
async def delete_team(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = TeamService(db)
    return await service.delete_team(team_id, current_user.tenant_id)


@router.post("/{team_id}/members")
async def add_member(
    team_id: uuid.UUID,
    data: TeamMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = TeamService(db)
    return await service.add_member(team_id, current_user.tenant_id, data)


@router.delete("/{team_id}/members/{user_id}")
async def remove_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = TeamService(db)
    return await service.remove_member(team_id, current_user.tenant_id, user_id)