import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class DatasetAnalysis(Base):
    __tablename__ = "dataset_analysis"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    quality_assessment: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    recommended_ml_task: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_column_candidate: Mapped[str | None] = mapped_column(String(255), nullable=True)
    insights: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    raw_llm_response: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="analysis")

    def __repr__(self) -> str:
        return f"<DatasetAnalysis dataset_id={self.dataset_id} task={self.recommended_ml_task}>"
