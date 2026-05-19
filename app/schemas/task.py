import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.task import PriorityType


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: uuid.UUID | None = None
    priority: PriorityType = PriorityType.MEDIUM
    due_date: datetime | None = None
    position: int = 0


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: uuid.UUID | None = None
    priority: PriorityType | None = None
    due_date: datetime | None = None


class TaskMove(BaseModel):
    column_id: uuid.UUID
    position: int


class TaskResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: uuid.UUID
    column_id: uuid.UUID
    assignee_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    priority: PriorityType
    due_date: datetime | None = None
    position: int
    created_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}