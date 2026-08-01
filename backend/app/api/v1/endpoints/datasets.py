from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dataset import DatasetResponse
from app.schemas.dataset_analysis import DatasetAnalysisResponse
from app.schemas.dataset_cleaning import DatasetCleaningResponse
from app.schemas.dataset_eda import DatasetEDAResponse
from app.schemas.dataset_profile import DatasetProfileResponse
from app.services.ai_analysis_service import AIAnalysisService
from app.services.cleaning_service import CleaningService
from app.services.dataset_service import DatasetService
from app.services.eda_service import EDAService
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


@router.get("/{dataset_id}/analysis", status_code=status.HTTP_200_OK)
async def get_dataset_analysis(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    ai_service = AIAnalysisService(db)
    analysis = await ai_service.get_dataset_analysis(dataset_id, current_user.id)
    data = DatasetAnalysisResponse.model_validate(analysis).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/{dataset_id}/cleaning-plan", status_code=status.HTTP_200_OK)
async def get_dataset_cleaning_plan(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    cleaning_service = CleaningService(db)
    cleaning = await cleaning_service.get_cleaning_plan(dataset_id, current_user.id)
    data = DatasetCleaningResponse.model_validate(cleaning).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post("/{dataset_id}/clean", status_code=status.HTTP_200_OK)
async def clean_dataset(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    cleaning_service = CleaningService(db)
    cleaning = await cleaning_service.execute_stored_cleaning_plan(dataset_id, current_user.id)
    data = DatasetCleaningResponse.model_validate(cleaning).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )



@router.get("/{dataset_id}/cleaned-file", status_code=status.HTTP_200_OK)
async def get_cleaned_dataset_file(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    cleaning_service = CleaningService(db)
    file_path, filename = await cleaning_service.get_cleaned_file_path(dataset_id, current_user.id)

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=filename,
    )


@router.get("/{dataset_id}/eda", status_code=status.HTTP_200_OK)
async def get_dataset_eda(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    eda_service = EDAService(db)
    eda = await eda_service.get_eda(dataset_id, current_user.id)
    data = DatasetEDAResponse.model_validate(eda).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/{dataset_id}/eda-report", status_code=status.HTTP_200_OK)
async def get_dataset_eda_report(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    eda_service = EDAService(db)
    file_path, filename = await eda_service.get_eda_report_path(dataset_id, current_user.id)

    return FileResponse(
        path=file_path,
        media_type="text/html",
        filename=filename,
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

