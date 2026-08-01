from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PreprocessDatasetRequest(BaseModel):
    target_column: str | None = None
    test_size: float = Field(default=0.2, ge=0.05, le=0.5)
    random_state: int = 42
    encode_categorical: dict[str, str] | None = None  # col -> "onehot" | "label" | "ordinal"
    scale_numeric: dict[str, str] | None = None       # col -> "standard" | "minmax" | "robust" | "normalize"
    feature_selection: dict[str, Any] | None = None   # e.g. {"method": "variance_threshold" | "k_best", "k": 10, "threshold": 0.01}


class DatasetPreprocessingResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    target_column: str | None
    preprocessing_plan: dict[str, Any]
    execution_summary: dict[str, Any] | None
    status: str
    ml_ready_path: str | None
    x_train_path: str | None
    x_test_path: str | None
    y_train_path: str | None
    y_test_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
