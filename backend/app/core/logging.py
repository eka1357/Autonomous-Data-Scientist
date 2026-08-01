import json
import sys
from loguru import logger
from app.core.config import settings


def _json_serializer(record: dict) -> str:
    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    if record["exception"]:
        log_data["exception"] = str(record["exception"])
    return json.dumps(log_data)


def setup_logging() -> None:
    logger.remove()

    if getattr(settings, "LOG_FORMAT", "text").lower() == "json" or settings.ENVIRONMENT == "production":
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=settings.LOG_LEVEL,
            serialize=True,
        )
    else:
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=settings.LOG_LEVEL,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
        )
