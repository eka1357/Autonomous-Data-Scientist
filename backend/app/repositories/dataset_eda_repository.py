from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_eda import DatasetEDA


class DatasetEDARepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dataset_id(self, dataset_id: UUID) -> DatasetEDA | None:
        stmt = select(DatasetEDA).where(DatasetEDA.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        dataset_id: UUID,
        summary: str,
        statistics: dict[str, Any],
        correlations: dict[str, Any],
        outliers: dict[str, Any],
        charts: dict[str, Any],
        insights: dict[str, Any],
        report_path: str | None = None,
    ) -> DatasetEDA:
        existing = await self.get_by_dataset_id(dataset_id)
        if existing:
            existing.summary = summary
            existing.statistics = statistics
            existing.correlations = correlations
            existing.outliers = outliers
            existing.charts = charts
            existing.insights = insights
            existing.report_path = report_path
            await self.session.flush()
            return existing

        eda = DatasetEDA(
            dataset_id=dataset_id,
            summary=summary,
            statistics=statistics,
            correlations=correlations,
            outliers=outliers,
            charts=charts,
            insights=insights,
            report_path=report_path,
        )
        self.session.add(eda)
        await self.session.flush()
        return eda
