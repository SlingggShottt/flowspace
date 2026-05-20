import uuid
from datetime import datetime
from pydantic import BaseModel


class CommentCreate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    id: str
    task_id: str
    tenant_id: str
    user_id: str
    user_name: str
    body: str
    created_at: datetime