from uuid import UUID
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AutoDSException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    TokenResponseData,
    UserLoginRequest,
    UserRegisterRequest,
    UserRegisterResponseData,
)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, data: UserRegisterRequest) -> UserRegisterResponseData:
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise AutoDSException(
                code="USER_ALREADY_EXISTS",
                message="User with this email already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        hashed_pw = hash_password(data.password)
        user = await self.user_repo.create(
            name=data.name,
            email=data.email,
            password_hash=hashed_pw,
        )
        await self.session.commit()

        return UserRegisterResponseData(
            user_id=user.id,
            message="Account created successfully",
        )

    async def authenticate_user(self, data: UserLoginRequest) -> TokenResponseData:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise AutoDSException(
                code="INVALID_CREDENTIALS",
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user_id_str = str(user.id)
        access_token = create_access_token(subject=user_id_str)
        refresh_token = create_refresh_token(subject=user_id_str)

        return TokenResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponseData:
        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise AutoDSException(
                code="INVALID_TOKEN",
                message="Invalid or expired refresh token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            ) from exc

        if payload.get("type") != "refresh":
            raise AutoDSException(
                code="INVALID_TOKEN",
                message="Token is not a valid refresh token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AutoDSException(
                code="INVALID_TOKEN",
                message="Invalid token payload",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user_uuid = UUID(user_id_str)
        except ValueError:
            raise AutoDSException(
                code="INVALID_TOKEN",
                message="Invalid user identifier in token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user = await self.user_repo.get_by_id(user_uuid)
        if not user:
            raise AutoDSException(
                code="USER_NOT_FOUND",
                message="User associated with token no longer exists",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        new_access_token = create_access_token(subject=user_id_str)
        new_refresh_token = create_refresh_token(subject=user_id_str)

        return TokenResponseData(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
