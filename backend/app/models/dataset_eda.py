from datetime import datetime, timezone
import uuid
from typing import Any, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class DatasetEDA(Base):
    __tablename__ = "dataset_eda"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    statistics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    correlations: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    outliers: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    charts: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    insights: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    report_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="eda")

    def __repr__(self) -> str:
        return f"<DatasetEDA id={self.id} dataset_id={self.dataset_id}>"
