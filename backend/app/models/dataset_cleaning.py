import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class DatasetCleaning(Base):
    __tablename__ = "dataset_cleanings"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    cleaning_plan: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    execution_summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending | in_progress | completed | failed

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="cleaning")

    def __repr__(self) -> str:
        return f"<DatasetCleaning dataset_id={self.dataset_id} status={self.status}>"
