from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    id: UUID
    project_id: UUID
    filename: str
    raw_storage_path: str
    cleaned_storage_path: str | None
    file_size_bytes: int
    file_type: str
    status: str
    row_count: int | None
    column_count: int | None
    uploaded_at: datetime
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)


class DatasetUploadResponseData(BaseModel):
    dataset_id: UUID
    filename: str
    file_size_bytes: int
    status: str
