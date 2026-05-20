from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.models.membership import Membership
from app.services.email_service import EmailService
from app.db.database import AsyncSessionLocal
from datetime import datetime, timezone


async def send_overdue_digests():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Membership))
            memberships = result.scalars().all()

            email_service = EmailService()

            for membership in memberships:
                user_result = await db.execute(
                    select(User).where(User.id == membership.user_id)
                )
                user = user_result.scalar_one_or_none()
                if not user:
                    continue

                tasks_result = await db.execute(
                    select(Task, Project).join(
                        Project, Task.project_id == Project.id
                    ).where(
                        Task.assignee_id == user.id,
                        Task.tenant_id == membership.tenant_id,
                        Task.deleted_at.is_(None),
                        Task.due_date < datetime.now(timezone.utc),
                    )
                )
                overdue = tasks_result.all()

                if not overdue:
                    continue

                overdue_list = [
                    {
                        "title": task.title,
                        "due_date": task.due_date.strftime("%d %b %Y"),
                        "project": project.name,
                    }
                    for task, project in overdue
                ]

                from app.repositories.tenant_repository import TenantRepository
                tenant_repo = TenantRepository(db)
                tenant = await tenant_repo.get_by_id(membership.tenant_id)

                email_service.send_overdue_digest_email(
                    to=user.email,
                    name=user.name,
                    overdue_tasks=overdue_list,
                    workspace_name=tenant.name if tenant else "Flowspace",
                )
        except Exception as e:
            print(f"Digest error: {e}")