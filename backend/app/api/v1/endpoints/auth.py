from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenRefreshRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    auth_service = AuthService(db)
    result = await auth_service.register_user(payload)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "data": result.model_dump(mode="json"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    auth_service = AuthService(db)
    tokens = await auth_service.authenticate_user(payload)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": tokens.model_dump(mode="json"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_tokens(payload.refresh_token)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": tokens.model_dump(mode="json"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": {"message": "Logged out successfully"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    user_data = UserResponse.model_validate(current_user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": user_data.model_dump(mode="json"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
