import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.task import Task
from app.models.column import Column
from app.repositories.team_repository import TeamRepository
from app.db.mongodb import get_mongodb


class DashboardService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, current_user: User) -> dict:
        is_admin = current_user.role == UserRole.ADMIN
        tenant_id = current_user.tenant_id

        projects = await self._get_projects(current_user)
        project_ids = [p.id for p in projects]

        now = datetime.now(timezone.utc)

        project_cards = []
        for project in projects:
            tasks_result = await self.db.execute(
                select(Task).where(
                    Task.project_id == project.id,
                    Task.tenant_id == tenant_id,
                    Task.deleted_at.is_(None),
                )
            )
            all_tasks = list(tasks_result.scalars().all())

            total_tasks = len(all_tasks)
            completed_tasks = await self._count_completed(project.id, tenant_id)
            overdue_tasks = len([
                t for t in all_tasks
                if t.due_date and t.due_date.replace(tzinfo=timezone.utc) < now
            ])

            if is_admin:
                card = {
                    "id": str(project.id),
                    "name": project.name,
                    "color": project.color,
                    "description": project.description,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "overdue_tasks": overdue_tasks,
                }
            else:
                assigned_tasks = [t for t in all_tasks if t.assignee_id == current_user.id]
                due_tasks = [
                    t for t in assigned_tasks
                    if t.due_date and t.due_date.replace(tzinfo=timezone.utc) >= now
                ]
                my_overdue = [
                    t for t in assigned_tasks
                    if t.due_date and t.due_date.replace(tzinfo=timezone.utc) < now
                ]
                my_completed = await self._count_completed_for_user(
                    project.id, tenant_id, current_user.id
                )
                card = {
                    "id": str(project.id),
                    "name": project.name,
                    "color": project.color,
                    "description": project.description,
                    "assigned_tasks": len(assigned_tasks),
                    "due_tasks": len(due_tasks),
                    "overdue_tasks": len(my_overdue),
                    "completed_tasks": my_completed,
                }

            project_cards.append(card)

        if is_admin:
            summary = await self._admin_summary(tenant_id, now)
        else:
            summary = await self._member_summary(tenant_id, current_user.id, now)

        recent_activity = await self._get_recent_activity(tenant_id)

        return {
            "is_admin": is_admin,
            "summary": summary,
            "projects": project_cards,
            "recent_activity": recent_activity,
        }

    async def _get_projects(self, current_user: User) -> list:
        from sqlalchemy import or_
        if current_user.role == UserRole.ADMIN:
            result = await self.db.execute(
                select(Project).where(
                    Project.tenant_id == current_user.tenant_id,
                    Project.archived_at.is_(None),
                ).order_by(Project.created_at.desc())
            )
            return list(result.scalars().all())
        else:
            team_repo = TeamRepository(self.db)
            user_teams = await team_repo.get_teams_for_user(
                current_user.id, current_user.tenant_id
            )
            team_ids = [t.id for t in user_teams]
            result = await self.db.execute(
                select(Project).where(
                    Project.tenant_id == current_user.tenant_id,
                    Project.archived_at.is_(None),
                    or_(Project.team_id.in_(team_ids), Project.team_id.is_(None)),
                ).order_by(Project.created_at.desc())
            )
            return list(result.scalars().all())

    async def _count_completed(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> int:
        done_columns_result = await self.db.execute(
            select(Column).where(
                Column.project_id == project_id,
                Column.name.ilike("%done%"),
            )
        )
        done_columns = list(done_columns_result.scalars().all())
        if not done_columns:
            return 0
        done_column_ids = [c.id for c in done_columns]
        result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.project_id == project_id,
                Task.tenant_id == tenant_id,
                Task.column_id.in_(done_column_ids),
                Task.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def _count_completed_for_user(
        self,
        project_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> int:
        done_columns_result = await self.db.execute(
            select(Column).where(
                Column.project_id == project_id,
                Column.name.ilike("%done%"),
            )
        )
        done_columns = list(done_columns_result.scalars().all())
        if not done_columns:
            return 0
        done_column_ids = [c.id for c in done_columns]
        result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.project_id == project_id,
                Task.tenant_id == tenant_id,
                Task.assignee_id == user_id,
                Task.column_id.in_(done_column_ids),
                Task.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def _admin_summary(self, tenant_id: uuid.UUID, now: datetime) -> dict:
        from app.models.membership import Membership
        members_result = await self.db.execute(
            select(func.count(Membership.id)).where(
                Membership.tenant_id == tenant_id,
            )
        )
        total_members = members_result.scalar() or 0

        projects_result = await self.db.execute(
            select(func.count(Project.id)).where(
                Project.tenant_id == tenant_id,
                Project.archived_at.is_(None),
            )
        )
        total_projects = projects_result.scalar() or 0

        tasks_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.tenant_id == tenant_id,
                Task.deleted_at.is_(None),
            )
        )
        total_tasks = tasks_result.scalar() or 0

        overdue_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.tenant_id == tenant_id,
                Task.deleted_at.is_(None),
                Task.due_date < now,
            )
        )
        total_overdue = overdue_result.scalar() or 0

        return {
            "total_members": total_members,
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "total_overdue": total_overdue,
        }

    async def _member_summary(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, now: datetime
    ) -> dict:
        assigned_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.tenant_id == tenant_id,
                Task.assignee_id == user_id,
                Task.deleted_at.is_(None),
            )
        )
        total_assigned = assigned_result.scalar() or 0

        overdue_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.tenant_id == tenant_id,
                Task.assignee_id == user_id,
                Task.deleted_at.is_(None),
                Task.due_date < now,
            )
        )
        total_overdue = overdue_result.scalar() or 0

        due_today_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.tenant_id == tenant_id,
                Task.assignee_id == user_id,
                Task.deleted_at.is_(None),
                Task.due_date >= now,
            )
        )
        due_soon = due_today_result.scalar() or 0

        return {
            "total_assigned": total_assigned,
            "total_overdue": total_overdue,
            "due_soon": due_soon,
        }

    async def _get_recent_activity(self, tenant_id: uuid.UUID) -> list:
        try:
            mongo = await get_mongodb()
            cursor = mongo.activities.find(
                {"tenant_id": str(tenant_id)}
            ).sort("created_at", -1).limit(5)
            activities = []
            async for doc in cursor:
                activities.append({
                    "task_id": doc.get("task_id"),
                    "user_name": doc.get("user_name"),
                    "action": doc.get("action"),
                    "detail": doc.get("detail"),
                    "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
                })
            return activities
        except Exception:
            return []