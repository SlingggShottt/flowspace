import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: uuid.UUID,
        email: str,
        name: str,
        password_hash: str,
        role: UserRole = UserRole.MEMBER,
        must_change_password: bool = False,
    ) -> User:
        user = User(
            tenant_id=tenant_id,
            email=email,
            name=name,
            password_hash=password_hash,
            role=role,
            must_change_password=must_change_password,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email_and_tenant(self, email: str, tenant_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email, User.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update_password(self, user: User, new_password_hash: str) -> User:
        user.password_hash = new_password_hash
        user.must_change_password = False
        await self.db.flush()
        return user