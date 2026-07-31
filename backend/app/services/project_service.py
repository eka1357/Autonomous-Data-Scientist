from uuid import UUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.project_repo = ProjectRepository(session)

    async def create_project(self, user_id: UUID, data: ProjectCreateRequest) -> Project:
        project = await self.project_repo.create(
            user_id=user_id,
            name=data.name,
            description=data.description,
        )
        await self.session.commit()
        return project

    async def get_project(self, project_id: UUID, user_id: UUID) -> Project:
        project = await self.project_repo.get_by_id(project_id, user_id)
        if not project:
            raise ResourceNotFoundException("Project not found or access denied")
        return project

    async def list_projects(self, user_id: UUID) -> list[Project]:
        return await self.project_repo.list_by_user(user_id)

    async def update_project(
        self, project_id: UUID, user_id: UUID, data: ProjectUpdateRequest
    ) -> Project:
        project = await self.get_project(project_id, user_id)
        updated_project = await self.project_repo.update(
            project, name=data.name, description=data.description
        )
        await self.session.commit()
        return updated_project

    async def delete_project(self, project_id: UUID, user_id: UUID) -> None:
        project = await self.get_project(project_id, user_id)
        await self.project_repo.delete(project)
        await self.session.commit()
