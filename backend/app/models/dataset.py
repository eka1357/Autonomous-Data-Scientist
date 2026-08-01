from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dataset_analysis import DatasetAnalysis
    from app.models.dataset_cleaning import DatasetCleaning
    from app.models.dataset_profile import DatasetProfile
    from app.models.project import Project


class Dataset(Base):
    __tablename__ = "datasets"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    cleaned_storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # csv | xlsx
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")  # uploaded | processing | completed | failed
    row_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    column_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship("Project", back_populates="datasets")
    profile: Mapped["DatasetProfile | None"] = relationship(
        "DatasetProfile", back_populates="dataset", uselist=False, cascade="all, delete-orphan"
    )
    analysis: Mapped["DatasetAnalysis | None"] = relationship(
        "DatasetAnalysis", back_populates="dataset", uselist=False, cascade="all, delete-orphan"
    )
    cleaning: Mapped["DatasetCleaning | None"] = relationship(
        "DatasetCleaning", back_populates="dataset", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Dataset id={self.id} filename={self.filename} status={self.status}>"
