from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_cleaning import DatasetCleaning


class DatasetCleaningRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dataset_id(self, dataset_id: UUID) -> DatasetCleaning | None:
        stmt = select(DatasetCleaning).where(DatasetCleaning.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        dataset_id: UUID,
        cleaning_plan: dict[str, Any],
        execution_summary: dict[str, Any] | None = None,
        status: str = "pending",
    ) -> DatasetCleaning:
        existing = await self.get_by_dataset_id(dataset_id)
        if existing:
            existing.cleaning_plan = cleaning_plan
            existing.execution_summary = execution_summary
            existing.status = status
            await self.session.flush()
            return existing

        cleaning = DatasetCleaning(
            dataset_id=dataset_id,
            cleaning_plan=cleaning_plan,
            execution_summary=execution_summary,
            status=status,
        )
        self.session.add(cleaning)
        await self.session.flush()
        return cleaning
