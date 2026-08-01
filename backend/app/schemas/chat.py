from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    stream: bool = False


class ChatMessageResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    user_id: UUID
    role: str
    content: str
    citations: list[dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageResponse]
