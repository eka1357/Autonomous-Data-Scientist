from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dataset import DatasetResponse
from app.schemas.dataset_profile import DatasetProfileResponse
from app.services.dataset_service import DatasetService
from app.services.profiling_service import ProfilingService

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    project_id: UUID = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    dataset_service = DatasetService(db)
    result = await dataset_service.upload_dataset(current_user.id, project_id, file)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "data": result.model_dump(mode="json"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/{dataset_id}", status_code=status.HTTP_200_OK)
async def get_dataset(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    dataset_service = DatasetService(db)
    dataset = await dataset_service.get_dataset(dataset_id, current_user.id)
    data = DatasetResponse.model_validate(dataset).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/{dataset_id}/profile", status_code=status.HTTP_200_OK)
async def get_dataset_profile(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    profiling_service = ProfilingService(db)
    profile = await profiling_service.get_dataset_profile(dataset_id, current_user.id)
    data = DatasetProfileResponse.model_validate(profile).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.delete("/{dataset_id}", status_code=status.HTTP_200_OK)
async def delete_dataset(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    dataset_service = DatasetService(db)
    await dataset_service.delete_dataset(dataset_id, current_user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": {"message": "Dataset deleted successfully"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
