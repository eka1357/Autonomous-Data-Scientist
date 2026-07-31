from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, project_id: UUID, user_id: UUID) -> Project | None:
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[Project]:
        stmt = select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_id: UUID, name: str, description: str | None = None) -> Project:
        project = Project(
            user_id=user_id,
            name=name.strip(),
            description=description.strip() if description else None,
        )
        self.session.add(project)
        await self.session.flush()
        return project

    async def update(self, project: Project, name: str | None = None, description: str | None = None) -> Project:
        if name is not None:
            project.name = name.strip()
        if description is not None:
            project.description = description.strip() if description else None
        await self.session.flush()
        return project

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.flush()
