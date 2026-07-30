from typing import Any
from loguru import logger
from app.worker.celery_app import celery_app


@celery_app.task(name="ping_task")
def ping_task(message: str = "pong") -> dict[str, Any]:
    logger.info(f"Executing ping_task with message: {message}")
    return {"status": "success", "message": message}
