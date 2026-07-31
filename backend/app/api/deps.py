from uuid import UUID
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AutoDSException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise AutoDSException(
            code="UNAUTHORIZED",
            message="Could not validate credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc

    if payload.get("type") != "access":
        raise AutoDSException(
            code="UNAUTHORIZED",
            message="Invalid token type",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AutoDSException(
            code="UNAUTHORIZED",
            message="Invalid token payload",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise AutoDSException(
            code="UNAUTHORIZED",
            message="Invalid user identifier in token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    repo = UserRepository(db)
    user = await repo.get_by_id(user_uuid)
    if not user:
        raise AutoDSException(
            code="UNAUTHORIZED",
            message="User not found",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return user
