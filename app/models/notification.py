import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    type: str
    title: str
    body: str | None = None
    is_read: bool
    task_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}