import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class ModelTraining(Base):
    __tablename__ = "model_trainings"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    problem_type: Mapped[str] = mapped_column(String(50), nullable=False)  # classification | regression | clustering
    target_column: Mapped[str | None] = mapped_column(String(255), nullable=True)
    best_algorithm: Mapped[str | None] = mapped_column(String(100), nullable=True)
    best_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    primary_metric: Mapped[str | None] = mapped_column(String(50), nullable=True)
    leaderboard: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default="[]")
    model_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending | in_progress | completed | failed

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="model_training")

    def __repr__(self) -> str:
        return f"<ModelTraining dataset_id={self.dataset_id} problem_type={self.problem_type} best={self.best_algorithm}>"
