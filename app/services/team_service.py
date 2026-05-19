import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.team_repository import TeamRepository
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberAdd, TeamResponse, TeamMemberResponse


class TeamService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TeamRepository(db)

    async def create_team(self, data: TeamCreate, tenant_id: uuid.UUID, user_id: uuid.UUID) -> TeamResponse:
        team = await self.repo.create(tenant_id=tenant_id, name=data.name, created_by=user_id)
        team = await self.repo.get_by_id(team.id, tenant_id)
        return TeamResponse.model_validate(team)

    async def list_teams(self, tenant_id: uuid.UUID) -> list[TeamResponse]:
        teams = await self.repo.get_all(tenant_id)
        return [TeamResponse.model_validate(t) for t in teams]

    async def update_team(self, team_id: uuid.UUID, tenant_id: uuid.UUID, data: TeamUpdate) -> TeamResponse:
        team = await self.repo.get_by_id(team_id, tenant_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        updated = await self.repo.update(team, data.name)
        updated = await self.repo.get_by_id(team_id, tenant_id)
        return TeamResponse.model_validate(updated)

    async def delete_team(self, team_id: uuid.UUID, tenant_id: uuid.UUID) -> dict:
        team = await self.repo.get_by_id(team_id, tenant_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        await self.repo.delete(team)
        return {"message": "Team deleted successfully"}

    async def add_member(self, team_id: uuid.UUID, tenant_id: uuid.UUID, data: TeamMemberAdd) -> TeamMemberResponse:
        team = await self.repo.get_by_id(team_id, tenant_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        member = await self.repo.add_member(team_id, data.user_id)
        return TeamMemberResponse.model_validate(member)

    async def remove_member(self, team_id: uuid.UUID, tenant_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        team = await self.repo.get_by_id(team_id, tenant_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        await self.repo.remove_member(team_id, user_id)
        return {"message": "Member removed from team"}