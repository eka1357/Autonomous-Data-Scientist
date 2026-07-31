from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DatasetProfileResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    column_names: list[str]
    data_types: dict[str, str]
    missing_values: dict[str, int]
    duplicate_row_count: int
    summary_stats: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
