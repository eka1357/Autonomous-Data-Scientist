from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DatasetAnalysisResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    summary: str
    quality_assessment: dict[str, Any]
    recommended_ml_task: str | None
    target_column_candidate: str | None
    insights: dict[str, Any]
    raw_llm_response: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
