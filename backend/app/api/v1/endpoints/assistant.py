from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageResponse, ChatRequest
from app.services.assistant_service import AssistantService

router = APIRouter()


@router.post("/datasets/{dataset_id}/chat", status_code=status.HTTP_200_OK)
async def chat_with_assistant(
    dataset_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AssistantService(db)

    if request.stream:
        return StreamingResponse(
            service.stream_chat_response(dataset_id, current_user.id, request.message),
            media_type="text/event-stream",
        )

    assistant_msg = await service.chat(dataset_id, current_user.id, request.message)
    data = ChatMessageResponse.model_validate(assistant_msg).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/datasets/{dataset_id}/chat/history", status_code=status.HTTP_200_OK)
async def get_chat_history(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    service = AssistantService(db)
    messages = await service.get_chat_history(dataset_id, current_user.id)
    data = [ChatMessageResponse.model_validate(m).model_dump(mode="json") for m in messages]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.delete("/datasets/{dataset_id}/chat/history", status_code=status.HTTP_200_OK)
async def clear_chat_history(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    service = AssistantService(db)
    await service.clear_chat_history(dataset_id, current_user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": {"message": "Chat history cleared successfully"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
