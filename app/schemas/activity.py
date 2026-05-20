# app/schemas/activity.py

from datetime import datetime
from pydantic import BaseModel


class ActivityResponse(BaseModel):
    id: str
    task_id: str
    tenant_id: str
    user_id: str
    user_name: str
    action: str
    detail: str | None = None
    created_at: datetime
