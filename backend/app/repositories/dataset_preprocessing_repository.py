from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_preprocessing import DatasetPreprocessing


class DatasetPreprocessingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dataset_id(self, dataset_id: UUID) -> DatasetPreprocessing | None:
        stmt = select(DatasetPreprocessing).where(DatasetPreprocessing.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        dataset_id: UUID,
        preprocessing_plan: dict[str, Any],
        target_column: str | None = None,
        execution_summary: dict[str, Any] | None = None,
        status: str = "pending",
        ml_ready_path: str | None = None,
        x_train_path: str | None = None,
        x_test_path: str | None = None,
        y_train_path: str | None = None,
        y_test_path: str | None = None,
    ) -> DatasetPreprocessing:
        existing = await self.get_by_dataset_id(dataset_id)
        if existing:
            existing.preprocessing_plan = preprocessing_plan
            if target_column is not None:
                existing.target_column = target_column
            if execution_summary is not None:
                existing.execution_summary = execution_summary
            existing.status = status
            if ml_ready_path is not None:
                existing.ml_ready_path = ml_ready_path
            if x_train_path is not None:
                existing.x_train_path = x_train_path
            if x_test_path is not None:
                existing.x_test_path = x_test_path
            if y_train_path is not None:
                existing.y_train_path = y_train_path
            if y_test_path is not None:
                existing.y_test_path = y_test_path
            await self.session.flush()
            return existing

        prep = DatasetPreprocessing(
            dataset_id=dataset_id,
            target_column=target_column,
            preprocessing_plan=preprocessing_plan,
            execution_summary=execution_summary,
            status=status,
            ml_ready_path=ml_ready_path,
            x_train_path=x_train_path,
            x_test_path=x_test_path,
            y_train_path=y_train_path,
            y_test_path=y_test_path,
        )
        self.session.add(prep)
        await self.session.flush()
        return prep
