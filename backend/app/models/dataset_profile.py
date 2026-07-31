import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class DatasetProfile(Base):
    __tablename__ = "dataset_profiles"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    column_names: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    data_types: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)
    missing_values: Mapped[dict[str, int]] = mapped_column(JSONB, nullable=False)
    duplicate_row_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    summary_stats: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="profile")

    def __repr__(self) -> str:
        return f"<DatasetProfile dataset_id={self.dataset_id} cols={len(self.column_names)}>"
