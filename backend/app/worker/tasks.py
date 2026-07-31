import asyncio
from typing import Any
from uuid import UUID
from loguru import logger

from app.db.session import AsyncSessionLocal
from app.services.profiling_service import ProfilingService
from app.worker.celery_app import celery_app


@celery_app.task(name="ping_task")
def ping_task(message: str = "pong") -> dict[str, Any]:
    logger.info(f"Executing ping_task with message: {message}")
    return {"status": "success", "message": message}


@celery_app.task(name="process_uploaded_dataset")
def process_uploaded_dataset(dataset_id: str) -> dict[str, Any]:
    logger.info(f"Executing profiling pipeline for dataset ID: {dataset_id}")

    async def _execute_profiling() -> None:
        async with AsyncSessionLocal() as session:
            service = ProfilingService(session)
            await service.run_profiling(UUID(dataset_id))

    try:
        asyncio.run(_execute_profiling())
        return {"status": "completed", "dataset_id": dataset_id}
    except Exception as exc:
        logger.error(f"Profiling task failed for dataset '{dataset_id}': {exc}")
        return {"status": "failed", "dataset_id": dataset_id, "error": str(exc)}
