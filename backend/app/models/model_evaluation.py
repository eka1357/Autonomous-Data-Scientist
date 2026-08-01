import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    feature_importance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    shap_values: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    report_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending | in_progress | completed | failed

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="evaluation")

    def __repr__(self) -> str:
        return f"<ModelEvaluation dataset_id={self.dataset_id} status={self.status}>"
