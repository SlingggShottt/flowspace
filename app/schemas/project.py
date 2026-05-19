import uuid
from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    color: str = "#6366f1"
    team_id: uuid.UUID | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    team_id: uuid.UUID | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    team_id: uuid.UUID | None = None
    name: str
    description: str | None = None
    color: str
    created_by: uuid.UUID | None = None
    created_at: datetime
    archived_at: datetime | None = None

    model_config = {"from_attributes": True}