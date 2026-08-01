from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.model_evaluation import ModelEvaluationResponse
from app.schemas.model_training import ModelTrainingResponse, TrainModelRequest
from app.services.automl_service import AutoMLService
from app.services.dataset_service import DatasetService
from app.services.evaluation_service import EvaluationService

router = APIRouter()


@router.post("/datasets/{dataset_id}/automl", status_code=status.HTTP_200_OK)
async def train_automl_models_endpoint(
    dataset_id: UUID,
    request: TrainModelRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    dataset_service = DatasetService(db)
    await dataset_service.get_dataset(dataset_id, current_user.id)

    automl_service = AutoMLService(db)
    target_col = request.target_column if request else None
    problem_type_override = request.problem_type if request else None

    mt_record = await automl_service.run_automl(
        dataset_id=dataset_id,
        target_column=target_col,
        problem_type_override=problem_type_override,
    )
    data = ModelTrainingResponse.model_validate(mt_record).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/datasets/{dataset_id}/models", status_code=status.HTTP_200_OK)
async def get_dataset_models_endpoint(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    automl_service = AutoMLService(db)
    mt = await automl_service.get_model_training(dataset_id, current_user.id)
    data = ModelTrainingResponse.model_validate(mt).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/datasets/{dataset_id}/models/download", status_code=status.HTTP_200_OK)
async def download_best_model_endpoint(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    automl_service = AutoMLService(db)
    file_path, filename = await automl_service.get_model_download_path(dataset_id, current_user.id)

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=filename,
    )


@router.post("/datasets/{dataset_id}/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_model_endpoint(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    dataset_service = DatasetService(db)
    await dataset_service.get_dataset(dataset_id, current_user.id)

    eval_service = EvaluationService(db)
    me_record = await eval_service.run_evaluation(dataset_id)
    data = ModelEvaluationResponse.model_validate(me_record).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/datasets/{dataset_id}/evaluation", status_code=status.HTTP_200_OK)
async def get_dataset_evaluation_endpoint(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    eval_service = EvaluationService(db)
    me = await eval_service.get_evaluation(dataset_id, current_user.id)
    data = ModelEvaluationResponse.model_validate(me).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/datasets/{dataset_id}/evaluation-report", status_code=status.HTTP_200_OK)
async def download_evaluation_report_endpoint(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    eval_service = EvaluationService(db)
    file_path, filename = await eval_service.get_evaluation_report_path(dataset_id, current_user.id)

    return FileResponse(
        path=file_path,
        media_type="text/html",
        filename=filename,
    )
