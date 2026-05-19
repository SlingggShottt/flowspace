import re
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tenant import Tenant, PlanType


class TenantRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str) -> Tenant:
        slug = self._generate_slug(name)
        slug = await self._ensure_unique_slug(slug)
        tenant = Tenant(name=name, slug=slug, plan=PlanType.FREE)
        self.db.add(tenant)
        await self.db.flush()
        return tenant

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Tenant | None:
        result = await self.db.execute(select(Tenant).where(Tenant.slug == slug))
        return result.scalar_one_or_none()

    def _generate_slug(self, name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s-]+", "-", slug)
        return slug.strip("-")[:50]

    async def _ensure_unique_slug(self, slug: str) -> str:
        base_slug = slug
        counter = 1
        while True:
            result = await self.db.execute(select(Tenant).where(Tenant.slug == slug))
            if not result.scalar_one_or_none():
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1