from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_profile import DatasetProfile


class DatasetProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dataset_id(self, dataset_id: UUID) -> DatasetProfile | None:
        stmt = select(DatasetProfile).where(DatasetProfile.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self, dataset_id: UUID, profile_data: dict[str, Any]
    ) -> DatasetProfile:
        existing = await self.get_by_dataset_id(dataset_id)
        if existing:
            existing.column_names = profile_data["column_names"]
            existing.data_types = profile_data["data_types"]
            existing.missing_values = profile_data["missing_values"]
            existing.duplicate_row_count = profile_data["duplicate_row_count"]
            existing.summary_stats = profile_data["summary_stats"]
            await self.session.flush()
            return existing

        profile = DatasetProfile(
            dataset_id=dataset_id,
            column_names=profile_data["column_names"],
            data_types=profile_data["data_types"],
            missing_values=profile_data["missing_values"],
            duplicate_row_count=profile_data["duplicate_row_count"],
            summary_stats=profile_data["summary_stats"],
        )
        self.session.add(profile)
        await self.session.flush()
        return profile
