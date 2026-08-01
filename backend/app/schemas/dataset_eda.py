from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DatasetEDAResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    summary: str
    statistics: dict[str, Any]
    correlations: dict[str, Any]
    outliers: dict[str, Any]
    charts: dict[str, Any]
    insights: dict[str, Any]
    report_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
