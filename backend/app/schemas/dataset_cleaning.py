from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CleanDatasetRequest(BaseModel):
    cleaning_plan: dict[str, Any] | None = None


class DatasetCleaningResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    cleaning_plan: dict[str, Any]
    execution_summary: dict[str, Any] | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
