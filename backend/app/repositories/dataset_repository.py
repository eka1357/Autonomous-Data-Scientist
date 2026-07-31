from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.dataset import Dataset
from app.models.project import Project


class DatasetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, dataset_id: UUID) -> Dataset | None:
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_user(self, dataset_id: UUID, user_id: UUID) -> Dataset | None:
        stmt = (
            select(Dataset)
            .join(Project, Dataset.project_id == Project.id)
            .where(Dataset.id == dataset_id, Project.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: UUID) -> list[Dataset]:
        stmt = select(Dataset).where(Dataset.project_id == project_id).order_by(Dataset.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        project_id: UUID,
        filename: str,
        raw_storage_path: str,
        file_size_bytes: int,
        file_type: str,
        status: str = "uploaded",
        uploaded_at: datetime | None = None,
    ) -> Dataset:
        dataset = Dataset(
            project_id=project_id,
            filename=filename,
            raw_storage_path=raw_storage_path,
            file_size_bytes=file_size_bytes,
            file_type=file_type,
            status=status,
            uploaded_at=uploaded_at or datetime.now(timezone.utc),
        )
        self.session.add(dataset)
        await self.session.flush()
        return dataset


    async def update_status(self, dataset_id: UUID, status: str) -> Dataset | None:
        dataset = await self.get_by_id(dataset_id)
        if dataset:
            dataset.status = status
            await self.session.flush()
        return dataset

    async def delete(self, dataset: Dataset) -> None:
        await self.session.delete(dataset)
        await self.session.flush()
