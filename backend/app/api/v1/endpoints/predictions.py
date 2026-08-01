import io
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.prediction import (
    BatchPredictionRequest,
    PredictionHistoryResponse,
    SinglePredictionRequest,
)
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/datasets/{dataset_id}/predict", status_code=status.HTTP_200_OK)
async def predict_single_endpoint(
    dataset_id: UUID,
    request: SinglePredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    service = PredictionService(db)
    history = await service.predict_single(dataset_id, current_user.id, request.inputs)
    data = PredictionHistoryResponse.model_validate(history).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post("/datasets/{dataset_id}/predict-batch", status_code=status.HTTP_200_OK)
async def predict_batch_endpoint(
    dataset_id: UUID,
    request: BatchPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    service = PredictionService(db)
    history = await service.predict_batch(dataset_id, current_user.id, request.samples)
    data = PredictionHistoryResponse.model_validate(history).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post("/datasets/{dataset_id}/predict-csv", status_code=status.HTTP_200_OK)
async def predict_csv_endpoint(
    dataset_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    service = PredictionService(db)
    history = await service.predict_csv(dataset_id, current_user.id, df)
    data = PredictionHistoryResponse.model_validate(history).model_dump(mode="json")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/predictions/{prediction_id}/download", status_code=status.HTTP_200_OK)
async def download_prediction_results_endpoint(
    prediction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    service = PredictionService(db)
    file_path, filename = await service.get_prediction_download(prediction_id, current_user.id)

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=filename,
    )


@router.get("/datasets/{dataset_id}/predictions", status_code=status.HTTP_200_OK)
async def get_dataset_predictions_history_endpoint(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    service = PredictionService(db)
    history_list = await service.get_history(dataset_id, current_user.id)
    data = [PredictionHistoryResponse.model_validate(h).model_dump(mode="json") for h in history_list]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
