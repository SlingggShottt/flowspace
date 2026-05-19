import uuid
from datetime import datetime
from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str


class TeamUpdate(BaseModel):
    name: str


class TeamMemberAdd(BaseModel):
    user_id: uuid.UUID


class TeamMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    team_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    created_at: datetime
    members: list[TeamMemberResponse] = []

    model_config = {"from_attributes": True}