import asyncio
from typing import Any
from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.services.ai_analysis_service import AIAnalysisService
from app.services.automl_service import AutoMLService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.evaluation_service import EvaluationService
from app.services.prediction_service import PredictionService
from app.services.preprocessing_service import PreprocessingService
from app.services.profiling_service import ProfilingService
from app.worker.celery_app import celery_app

_worker_engine = None
_worker_session_maker = None


def get_worker_session_maker() -> async_sessionmaker[AsyncSession]:
    global _worker_engine, _worker_session_maker
    if _worker_session_maker is None:
        db_url = (
            settings.DATABASE_URL
            or "postgresql+asyncpg://autods_user:autods_password@postgres:5432/autods_db"
        )
        _worker_engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        _worker_session_maker = async_sessionmaker(
            bind=_worker_engine, class_=AsyncSession, expire_on_commit=False
        )
    return _worker_session_maker


@celery_app.task(name="ping_task")
def ping_task(message: str = "pong") -> dict[str, Any]:
    logger.info(f"Executing ping_task with message: {message}")
    return {"status": "success", "message": message}


@celery_app.task(name="process_uploaded_dataset")
def process_uploaded_dataset(dataset_id: str) -> dict[str, Any]:
    logger.info(
        f"Executing full pipeline (profiling + AI analysis + cleaning + EDA + preprocessing + AutoML + evaluation) for dataset ID: {dataset_id}"
    )

    async def _execute_pipeline() -> None:
        session_maker = get_worker_session_maker()
        async with session_maker() as session:
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

            # 5. Preprocess & Feature Engineering for ML
            prep_service = PreprocessingService(session)
            await prep_service.run_preprocessing(dataset_uuid)

            # 6. AutoML Training
            automl_service = AutoMLService(session)
            await automl_service.run_automl(dataset_uuid)

            # 7. Model Evaluation & Report Generation
            eval_service = EvaluationService(session)
            await eval_service.run_evaluation(dataset_uuid)

    try:
        asyncio.run(_execute_pipeline())
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        logger.error(f"Dataset pipeline failed for dataset '{dataset_id}': {exc}")
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}


@celery_app.task(name="preprocess_dataset_task")
def preprocess_dataset_task(
    dataset_id: str, custom_plan: dict[str, Any] | None = None, target_column: str | None = None
) -> dict[str, Any]:
    logger.info(f"Executing standalone preprocessing task for dataset ID: {dataset_id}")

    async def _execute_preprocessing() -> None:
        session_maker = get_worker_session_maker()
        async with session_maker() as session:
            dataset_uuid = UUID(dataset_id)
            prep_service = PreprocessingService(session)
            await prep_service.run_preprocessing(
                dataset_id=dataset_uuid, custom_plan=custom_plan, target_column=target_column
            )

    try:
        asyncio.run(_execute_preprocessing())
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        logger.error(f"Preprocessing task failed for dataset '{dataset_id}': {exc}")
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}


@celery_app.task(name="train_models_task")
def train_models_task(
    dataset_id: str, target_column: str | None = None, problem_type_override: str | None = None
) -> dict[str, Any]:
    logger.info(f"Executing standalone AutoML training task for dataset ID: {dataset_id}")

    async def _execute_training() -> None:
        session_maker = get_worker_session_maker()
        async with session_maker() as session:
            dataset_uuid = UUID(dataset_id)
            automl_service = AutoMLService(session)
            await automl_service.run_automl(
                dataset_id=dataset_uuid,
                target_column=target_column,
                problem_type_override=problem_type_override,
            )

    try:
        asyncio.run(_execute_training())
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        logger.error(f"AutoML training task failed for dataset '{dataset_id}': {exc}")
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}


@celery_app.task(name="evaluate_model_task")
def evaluate_model_task(dataset_id: str) -> dict[str, Any]:
    logger.info(f"Executing standalone model evaluation task for dataset ID: {dataset_id}")

    async def _execute_evaluation() -> None:
        session_maker = get_worker_session_maker()
        async with session_maker() as session:
            dataset_uuid = UUID(dataset_id)
            eval_service = EvaluationService(session)
            await eval_service.run_evaluation(dataset_uuid)

    try:
        asyncio.run(_execute_evaluation())
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        logger.error(f"Model evaluation task failed for dataset '{dataset_id}': {exc}")
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}


@celery_app.task(name="predict_batch_task")
def predict_batch_task(
    dataset_id: str, user_id: str, samples: list[dict[str, Any]]
) -> dict[str, Any]:
    logger.info(f"Executing batch prediction Celery task for dataset ID: {dataset_id}")

    async def _execute_predict() -> None:
        session_maker = get_worker_session_maker()
        async with session_maker() as session:
            dataset_uuid = UUID(dataset_id)
            user_uuid = UUID(user_id)
            pred_service = PredictionService(session)
            await pred_service.predict_batch(dataset_uuid, user_uuid, samples)

    try:
        asyncio.run(_execute_predict())
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        logger.error(f"Batch prediction task failed for dataset '{dataset_id}': {exc}")
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}
