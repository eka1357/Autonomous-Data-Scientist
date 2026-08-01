from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_training import ModelTraining


class ModelTrainingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_dataset_id(self, dataset_id: UUID) -> ModelTraining | None:
        stmt = select(ModelTraining).where(ModelTraining.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        dataset_id: UUID,
        problem_type: str,
        target_column: str | None = None,
        best_algorithm: str | None = None,
        best_score: float | None = None,
        primary_metric: str | None = None,
        leaderboard: list[dict[str, Any]] | None = None,
        model_path: str | None = None,
        status: str = "pending",
    ) -> ModelTraining:
        existing = await self.get_by_dataset_id(dataset_id)
        if existing:
            existing.problem_type = problem_type
            if target_column is not None:
                existing.target_column = target_column
            if best_algorithm is not None:
                existing.best_algorithm = best_algorithm
            if best_score is not None:
                existing.best_score = best_score
            if primary_metric is not None:
                existing.primary_metric = primary_metric
            if leaderboard is not None:
                existing.leaderboard = leaderboard
            if model_path is not None:
                existing.model_path = model_path
            existing.status = status
            await self.session.flush()
            return existing

        mt = ModelTraining(
            dataset_id=dataset_id,
            problem_type=problem_type,
            target_column=target_column,
            best_algorithm=best_algorithm,
            best_score=best_score,
            primary_metric=primary_metric,
            leaderboard=leaderboard or [],
            model_path=model_path,
            status=status,
        )
        self.session.add(mt)
        await self.session.flush()
        return mt
