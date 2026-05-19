import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.column import Column


class ColumnRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: uuid.UUID,
        project_id: uuid.UUID,
        name: str,
        position: int = 0,
    ) -> Column:
        column = Column(
            tenant_id=tenant_id,
            project_id=project_id,
            name=name,
            position=position,
        )
        self.db.add(column)
        await self.db.flush()
        return column

    async def get_by_id(self, column_id: uuid.UUID, tenant_id: uuid.UUID) -> Column | None:
        result = await self.db.execute(
            select(Column).where(
                Column.id == column_id,
                Column.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> list[Column]:
        result = await self.db.execute(
            select(Column).where(
                Column.project_id == project_id,
                Column.tenant_id == tenant_id,
            ).order_by(Column.position.asc())
        )
        return list(result.scalars().all())

    async def update(self, column: Column, **kwargs) -> Column:
        for key, value in kwargs.items():
            if value is not None:
                setattr(column, key, value)
        await self.db.flush()
        return column

    async def delete(self, column: Column) -> None:
        await self.db.delete(column)
        await self.db.flush()