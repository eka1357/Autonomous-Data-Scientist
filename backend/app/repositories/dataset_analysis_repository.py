from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_analysis import DatasetAnalysis


class DatasetAnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dataset_id(self, dataset_id: UUID) -> DatasetAnalysis | None:
        stmt = select(DatasetAnalysis).where(DatasetAnalysis.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        dataset_id: UUID,
        summary: str,
        quality_assessment: dict[str, Any],
        recommended_ml_task: str | None,
        target_column_candidate: str | None,
        insights: dict[str, Any],
        raw_llm_response: dict[str, Any] | None = None,
    ) -> DatasetAnalysis:
        existing = await self.get_by_dataset_id(dataset_id)
        if existing:
            existing.summary = summary
            existing.quality_assessment = quality_assessment
            existing.recommended_ml_task = recommended_ml_task
            existing.target_column_candidate = target_column_candidate
            existing.insights = insights
            existing.raw_llm_response = raw_llm_response
            await self.session.flush()
            return existing

        analysis = DatasetAnalysis(
            dataset_id=dataset_id,
            summary=summary,
            quality_assessment=quality_assessment,
            recommended_ml_task=recommended_ml_task,
            target_column_candidate=target_column_candidate,
            insights=insights,
            raw_llm_response=raw_llm_response,
        )
        self.session.add(analysis)
        await self.session.flush()
        return analysis
