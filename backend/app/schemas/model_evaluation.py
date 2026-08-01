from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ModelEvaluationResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    metrics: dict[str, Any]
    feature_importance: dict[str, Any]
    shap_values: dict[str, Any]
    report_path: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
