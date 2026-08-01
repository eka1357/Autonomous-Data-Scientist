import asyncio
from typing import Any
from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.services.ai_analysis_service import AIAnalysisService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.profiling_service import ProfilingService
from app.worker.celery_app import celery_app


@celery_app.task(name="ping_task")
def ping_task(message: str = "pong") -> dict[str, Any]:
    logger.info(f"Executing ping_task with message: {message}")
    return {"status": "success", "message": message}


@celery_app.task(name="process_uploaded_dataset")
def process_uploaded_dataset(dataset_id: str) -> dict[str, Any]:
    logger.info(f"Executing pipeline (profiling + AI analysis + cleaning + EDA) for dataset ID: {dataset_id}")

    async def _execute_pipeline() -> None:
        db_url = (
            settings.DATABASE_URL
            or "postgresql+asyncpg://autods_user:autods_password@postgres:5432/autods_db"
        )
        task_engine = create_async_engine(db_url, pool_pre_ping=True)
        task_session_maker = async_sessionmaker(
            bind=task_engine, class_=AsyncSession, expire_on_commit=False
        )

        try:
            async with task_session_maker() as session:
                dataset_uuid = UUID(dataset_id)

                # 1. Profile Dataset
                profiling_service = ProfilingService(session)
                await profiling_service.run_profiling(dataset_uuid)

                # 2. Generate AI Analysis
                ai_service = AIAnalysisService(session)
                await ai_service.generate_analysis(dataset_uuid)

                # 3. Generate & Execute AI Cleaning Plan
                cleaning_service = CleaningService(session)
                await cleaning_service.generate_and_execute_cleaning(dataset_uuid)

                # 4. Generate Exploratory Data Analysis (EDA) & Charts
                eda_service = EDAService(session)
                await eda_service.run_eda(dataset_uuid)
        finally:
            await task_engine.dispose()


    try:
        asyncio.run(_execute_pipeline())
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        logger.error(f"Dataset pipeline failed for dataset '{dataset_id}': {exc}")
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}
