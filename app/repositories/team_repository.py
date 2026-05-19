import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.team import Team, TeamMember


class TeamRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tenant_id: uuid.UUID, name: str, created_by: uuid.UUID) -> Team:
        team = Team(tenant_id=tenant_id, name=name, created_by=created_by)
        self.db.add(team)
        await self.db.flush()
        return team

    async def get_by_id(self, team_id: uuid.UUID, tenant_id: uuid.UUID) -> Team | None:
        result = await self.db.execute(
            select(Team)
            .options(selectinload(Team.members))
            .where(Team.id == team_id, Team.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, tenant_id: uuid.UUID) -> list[Team]:
        result = await self.db.execute(
            select(Team)
            .options(selectinload(Team.members))
            .where(Team.tenant_id == tenant_id)
            .order_by(Team.created_at.asc())
        )
        return list(result.scalars().all())

    async def update(self, team: Team, name: str) -> Team:
        team.name = name
        await self.db.flush()
        return team

    async def delete(self, team: Team) -> None:
        await self.db.delete(team)
        await self.db.flush()

    async def add_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> TeamMember:
        member = TeamMember(team_id=team_id, user_id=user_id)
        self.db.add(member)
        await self.db.flush()
        return member

    async def remove_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if member:
            await self.db.delete(member)
            await self.db.flush()

    async def get_teams_for_user(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> list[Team]:
        result = await self.db.execute(
            select(Team)
            .join(TeamMember, TeamMember.team_id == Team.id)
            .where(TeamMember.user_id == user_id, Team.tenant_id == tenant_id)
        )
        return list(result.scalars().all())