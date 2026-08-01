import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.user import User


class PredictionHistory(Base):
    __tablename__ = "prediction_histories"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # single | batch
    input_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    output_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    result_file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="predictions")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<PredictionHistory id={self.id} type={self.prediction_type} status={self.status}>"
