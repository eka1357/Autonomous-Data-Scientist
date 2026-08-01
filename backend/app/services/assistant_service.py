import asyncio
from typing import AsyncGenerator
from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.core.rag_engine import assemble_dataset_rag_context, generate_rag_response
from app.models.chat_message import ChatMessage
from app.repositories.chat_repository import ChatRepository
from app.repositories.dataset_analysis_repository import DatasetAnalysisRepository
from app.repositories.dataset_cleaning_repository import DatasetCleaningRepository
from app.repositories.dataset_eda_repository import DatasetEDARepository
from app.repositories.dataset_preprocessing_repository import DatasetPreprocessingRepository
from app.repositories.dataset_profile_repository import DatasetProfileRepository
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.model_evaluation_repository import ModelEvaluationRepository
from app.repositories.model_training_repository import ModelTrainingRepository


class AssistantService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = DatasetProfileRepository(session)
        self.analysis_repo = DatasetAnalysisRepository(session)
        self.cleaning_repo = DatasetCleaningRepository(session)
        self.eda_repo = DatasetEDARepository(session)
        self.prep_repo = DatasetPreprocessingRepository(session)
        self.mt_repo = ModelTrainingRepository(session)
        self.me_repo = ModelEvaluationRepository(session)
        self.chat_repo = ChatRepository(session)

    async def _build_dataset_context(self, dataset_id: UUID) -> tuple[str, list[dict[str, str]]]:
        profile = await self.profile_repo.get_by_dataset_id(dataset_id)
        analysis = await self.analysis_repo.get_by_dataset_id(dataset_id)
        cleaning = await self.cleaning_repo.get_by_dataset_id(dataset_id)
        eda = await self.eda_repo.get_by_dataset_id(dataset_id)
        prep = await self.prep_repo.get_by_dataset_id(dataset_id)
        mt = await self.mt_repo.get_by_dataset_id(dataset_id)
        me = await self.me_repo.get_by_dataset_id(dataset_id)

        profile_dict = {"column_names": profile.column_names, "data_types": profile.data_types, "missing": profile.missing_values} if profile else None
        analysis_dict = {"summary": analysis.summary, "task": analysis.recommended_ml_task, "target": analysis.target_column_candidate} if analysis else None
        cleaning_dict = {"plan": cleaning.cleaning_plan, "summary": cleaning.execution_summary} if cleaning else None
        eda_dict = {"summary": eda.summary, "insights": eda.insights, "outliers": eda.outliers} if eda else None
        prep_dict = {"plan": prep.preprocessing_plan, "summary": prep.execution_summary} if prep else None
        mt_dict = {"problem_type": mt.problem_type, "best_algorithm": mt.best_algorithm, "score": mt.best_score, "leaderboard": mt.leaderboard} if mt else None
        me_dict = {"metrics": me.metrics, "feature_importance": me.feature_importance, "shap": me.shap_values} if me else None

        return assemble_dataset_rag_context(
            profile_dict, analysis_dict, cleaning_dict, eda_dict, prep_dict, mt_dict, me_dict
        )

    async def chat(
        self, dataset_id: UUID, user_id: UUID, message: str
    ) -> ChatMessage:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        # Save user message
        await self.chat_repo.create(dataset_id, user_id, "user", message)

        # Build context & history
        context_str, available_citations = await self._build_dataset_context(dataset_id)
        history_msgs = await self.chat_repo.list_by_dataset_and_user(dataset_id, user_id)
        history_formatted = [{"role": m.role, "content": m.content} for m in history_msgs]

        # Generate response
        response_text = await generate_rag_response(message, context_str, history_formatted)

        # Save assistant message
        assistant_msg = await self.chat_repo.create(
            dataset_id, user_id, "assistant", response_text, citations=available_citations
        )
        await self.session.commit()
        return assistant_msg

    async def stream_chat_response(
        self, dataset_id: UUID, user_id: UUID, message: str
    ) -> AsyncGenerator[str, None]:
        try:
            assistant_msg = await self.chat(dataset_id, user_id, message)
            full_text = assistant_msg.content

            # Stream words in chunks for real-time streaming simulation
            words = full_text.split()
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i : i + 3]) + " "
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.05)
            yield "data: [DONE]\n\n"
        except Exception as exc:
            logger.error(f"Error in stream_chat_response for dataset '{dataset_id}': {exc}")
            yield f"data: [ERROR] {str(exc)}\n\n"
            yield "data: [DONE]\n\n"

    async def get_chat_history(self, dataset_id: UUID, user_id: UUID) -> list[ChatMessage]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        return await self.chat_repo.list_by_dataset_and_user(dataset_id, user_id)

    async def clear_chat_history(self, dataset_id: UUID, user_id: UUID) -> None:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        await self.chat_repo.delete_history(dataset_id, user_id)
        await self.session.commit()
