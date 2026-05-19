import uuid
from sqlalchemy import String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TimeStampedBase
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class User(TimeStampedBase):
    __tablename__ = "users"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.MEMBER, nullable=False)

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="user")
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", back_populates="assignee")