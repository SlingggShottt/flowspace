import uuid
from datetime import datetime
from pydantic import BaseModel


class ColumnCreate(BaseModel):
    name: str
    position: int = 0


class ColumnUpdate(BaseModel):
    name: str | None = None
    position: int | None = None


class ColumnResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    position: int
    created_at: datetime

    model_config = {"from_attributes": True}