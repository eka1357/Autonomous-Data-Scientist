import asyncio
from typing import Any
from loguru import logger
from sqlalchemy import text

from app.db.session import engine
from app.worker.celery_app import celery_app



@celery_app.task(name="ping_task")
def ping_task(message: str = "pong") -> dict[str, Any]:
    logger.info(f"Executing ping_task with message: {message}")
    return {"status": "success", "message": message}


@celery_app.task(name="process_uploaded_dataset")
def process_uploaded_dataset(dataset_id: str) -> dict[str, Any]:
    logger.info(f"Processing uploaded dataset ID: {dataset_id}")

    async def _update_status() -> None:
        async with engine.begin() as conn:
            await conn.execute(
                text("UPDATE datasets SET status = 'completed' WHERE id = :dataset_id"),
                {"dataset_id": dataset_id},
            )

    try:
        asyncio.run(_update_status())
    except Exception as exc:
        logger.warning(f"Celery dataset status update note: {exc}")

    return {"status": "completed", "dataset_id": dataset_id}

