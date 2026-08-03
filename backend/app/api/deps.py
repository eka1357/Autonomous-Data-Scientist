from uuid import UUID
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AutoDSException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository

DEFAULT_USER_EMAIL = "default@autods.local"
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000000")
DEFAULT_PROJECT_ID = UUID("00000000-0000-0000-0000-000000000000")

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    repo = UserRepository(db)

    if credentials and credentials.credentials:
        token = credentials.credentials
        try:
            payload = decode_token(token)
            if payload.get("type") == "access":
                user_id_str = payload.get("sub")
                if user_id_str:
                    user_uuid = UUID(user_id_str)
                    user = await repo.get_by_id(user_uuid)
                    if user:
                        return user
        except Exception:
            pass

    # Default fallback user for local single-user workspace execution
    user = await repo.get_by_email(DEFAULT_USER_EMAIL)
    if not user:
        user = await repo.create(
            name="Default Workspace User",
            email=DEFAULT_USER_EMAIL,
            password_hash="disabled",
        )
        proj_repo = ProjectRepository(db)
        project = await proj_repo.get_by_id(DEFAULT_PROJECT_ID, user.id)
        if not project:
            await proj_repo.create(
                user_id=user.id,
                name="Default Project",
                description="Default Workspace Project",
            )
        await db.commit()

    return user

