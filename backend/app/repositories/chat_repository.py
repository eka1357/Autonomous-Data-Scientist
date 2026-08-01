from typing import Any
from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_dataset_and_user(
        self, dataset_id: UUID, user_id: UUID
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.dataset_id == dataset_id, ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        dataset_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        citations: list[dict[str, Any]] | None = None,
    ) -> ChatMessage:
        msg = ChatMessage(
            dataset_id=dataset_id,
            user_id=user_id,
            role=role,
            content=content,
            citations=citations or [],
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def delete_history(self, dataset_id: UUID, user_id: UUID) -> None:
        stmt = delete(ChatMessage).where(
            ChatMessage.dataset_id == dataset_id, ChatMessage.user_id == user_id
        )
        await self.session.execute(stmt)
        await self.session.flush()
