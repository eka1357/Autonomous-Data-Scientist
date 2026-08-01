from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SinglePredictionRequest(BaseModel):
    inputs: dict[str, Any]


class BatchPredictionRequest(BaseModel):
    samples: list[dict[str, Any]]


class PredictionResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    prediction_type: str
    predictions: list[Any]
    probabilities: list[Any] | None = None
    result_file_path: str | None = None
    created_at: datetime


class PredictionHistoryResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    user_id: UUID
    prediction_type: str
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]
    result_file_path: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
