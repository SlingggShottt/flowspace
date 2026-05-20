# app/services/activity_service.py

import uuid
from datetime import datetime, timezone
from app.db.mongodb import get_mongodb
from app.schemas.activity import ActivityResponse


class ActivityService:

    async def log_activity(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        user_name: str,
        action: str,
        detail: str | None = None,
    ) -> None:
        db = await get_mongodb()
        await db.activities.insert_one({
            "task_id": str(task_id),
            "tenant_id": str(tenant_id),
            "user_id": str(user_id),
            "user_name": user_name,
            "action": action,
            "detail": detail,
            "created_at": datetime.now(timezone.utc),
        })

    async def get_activity(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> list[ActivityResponse]:
        db = await get_mongodb()
        cursor = db.activities.find(
            {"task_id": str(task_id), "tenant_id": str(tenant_id)}
        ).sort("created_at", -1).limit(50)
        activities = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            activities.append(ActivityResponse(**doc))
        return activities
