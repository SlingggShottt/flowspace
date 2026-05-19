import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.tenant import PlanType


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: PlanType
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceUpdate(BaseModel):
    name: str | None = None