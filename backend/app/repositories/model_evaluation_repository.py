from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_evaluation import ModelEvaluation


class ModelEvaluationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dataset_id(self, dataset_id: UUID) -> ModelEvaluation | None:
        stmt = select(ModelEvaluation).where(ModelEvaluation.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        dataset_id: UUID,
        metrics: dict[str, Any],
        feature_importance: dict[str, Any],
        shap_values: dict[str, Any],
        report_path: str | None = None,
        status: str = "pending",
    ) -> ModelEvaluation:
        existing = await self.get_by_dataset_id(dataset_id)
        if existing:
            existing.metrics = metrics
            existing.feature_importance = feature_importance
            existing.shap_values = shap_values
            if report_path is not None:
                existing.report_path = report_path
            existing.status = status
            await self.session.flush()
            return existing

        me = ModelEvaluation(
            dataset_id=dataset_id,
            metrics=metrics,
            feature_importance=feature_importance,
            shap_values=shap_values,
            report_path=report_path,
            status=status,
        )
        self.session.add(me)
        await self.session.flush()
        return me
