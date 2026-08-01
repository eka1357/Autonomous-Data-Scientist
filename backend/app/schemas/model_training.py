from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TrainModelRequest(BaseModel):
    target_column: str | None = None
    problem_type: str | None = None  # classification | regression | clustering (optional override)


class ModelTrainingResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    problem_type: str
    target_column: str | None
    best_algorithm: str | None
    best_score: float | None
    primary_metric: str | None
    leaderboard: list[dict[str, Any]]
    model_path: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
