from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TimeStampedBase
import enum


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(TimeStampedBase):
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[PlanType] = mapped_column(SAEnum(PlanType), default=PlanType.FREE, nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="tenant")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="tenant")
    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="tenant")