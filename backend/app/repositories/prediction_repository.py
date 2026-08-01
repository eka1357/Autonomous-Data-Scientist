from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction_history import PredictionHistory


class PredictionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, prediction_id: UUID) -> PredictionHistory | None:
        stmt = select(PredictionHistory).where(PredictionHistory.id == prediction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_dataset_and_user(
        self, dataset_id: UUID, user_id: UUID
    ) -> list[PredictionHistory]:
        stmt = (
            select(PredictionHistory)
            .where(PredictionHistory.dataset_id == dataset_id, PredictionHistory.user_id == user_id)
            .order_by(PredictionHistory.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        dataset_id: UUID,
        user_id: UUID,
        prediction_type: str,
        input_summary: dict[str, Any],
        output_summary: dict[str, Any],
        result_file_path: str | None = None,
        status: str = "completed",
    ) -> PredictionHistory:
        history = PredictionHistory(
            dataset_id=dataset_id,
            user_id=user_id,
            prediction_type=prediction_type,
            input_summary=input_summary,
            output_summary=output_summary,
            result_file_path=result_file_path,
            status=status,
        )
        self.session.add(history)
        await self.session.flush()
        return history
