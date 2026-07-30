from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/health", response_model=None)
async def health_check(db: AsyncSession = Depends(get_db)) -> Any:
    db_status = "down"
    redis_status = "down"

    # Verify PostgreSQL DB connection
    try:
        await db.execute(text("SELECT 1"))
        db_status = "up"
    except Exception:
        db_status = "down"

    # Verify Redis connection
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        if await redis_client.ping():
            redis_status = "up"
        await redis_client.aclose()
    except Exception:
        redis_status = "down"

    is_healthy = db_status == "up" and redis_status == "up"
    http_status = status.HTTP_200_OK if is_healthy else status.HTTP_530_SITE_IS_FROZEN

    return JSONResponse(
        status_code=http_status,
        content={
            "success": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy",
            "services": {
                "database": db_status,
                "redis": redis_status,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
