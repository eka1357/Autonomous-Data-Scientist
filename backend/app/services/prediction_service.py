import os
import uuid
from typing import Any
from uuid import UUID
import joblib
from loguru import logger
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.core.predictor import predict_with_model
from app.models.prediction_history import PredictionHistory
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.model_training_repository import ModelTrainingRepository
from app.repositories.prediction_repository import PredictionRepository


class PredictionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.mt_repo = ModelTrainingRepository(session)
        self.pred_repo = PredictionRepository(session)

    async def _load_trained_model(self, dataset_id: UUID, user_id: UUID) -> tuple[Any, str]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        mt = await self.mt_repo.get_by_dataset_id(dataset_id)
        if not mt or not mt.model_path or not os.path.exists(mt.model_path):
            raise ResourceNotFoundException(f"Trained model binary for dataset '{dataset_id}' not found")

        model = joblib.load(mt.model_path)
        return model, dataset.filename

    async def predict_single(
        self, dataset_id: UUID, user_id: UUID, inputs: dict[str, Any]
    ) -> PredictionHistory:
        model, _ = await self._load_trained_model(dataset_id, user_id)
        input_df = pd.DataFrame([inputs])

        preds, probas = predict_with_model(model, input_df)

        input_summary = {"feature_count": len(inputs), "sample_count": 1}
        output_summary = {
            "prediction": preds[0],
            "probability": probas[0] if probas else None,
        }

        history = await self.pred_repo.create(
            dataset_id=dataset_id,
            user_id=user_id,
            prediction_type="single",
            input_summary=input_summary,
            output_summary=output_summary,
            result_file_path=None,
            status="completed",
        )
        await self.session.commit()
        logger.info(f"Single prediction executed for dataset '{dataset_id}' -> result: {preds[0]}")
        return history

    async def predict_batch(
        self, dataset_id: UUID, user_id: UUID, samples: list[dict[str, Any]]
    ) -> PredictionHistory:
        model, filename = await self._load_trained_model(dataset_id, user_id)
        input_df = pd.DataFrame(samples)

        preds, probas = predict_with_model(model, input_df)

        result_df = input_df.copy()
        result_df["prediction"] = preds

        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        pred_dir = os.path.join(base_dir, "predictions", str(dataset_id))
        os.makedirs(pred_dir, exist_ok=True)

        history_id_temp = str(uuid.uuid4())
        result_file = os.path.join(pred_dir, f"prediction_{history_id_temp}.csv")
        result_df.to_csv(result_file, index=False)

        input_summary = {"feature_count": len(input_df.columns), "sample_count": len(input_df)}
        output_summary = {
            "prediction_count": len(preds),
            "sample_predictions": preds[:5],
        }

        history = await self.pred_repo.create(
            dataset_id=dataset_id,
            user_id=user_id,
            prediction_type="batch",
            input_summary=input_summary,
            output_summary=output_summary,
            result_file_path=result_file,
            status="completed",
        )
        await self.session.commit()
        logger.info(f"Batch prediction executed for dataset '{dataset_id}' ({len(samples)} samples)")
        return history

    async def predict_csv(
        self, dataset_id: UUID, user_id: UUID, df: pd.DataFrame
    ) -> PredictionHistory:
        samples = df.to_dict(orient="records")
        return await self.predict_batch(dataset_id, user_id, samples)

    async def get_history(self, dataset_id: UUID, user_id: UUID) -> list[PredictionHistory]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        return await self.pred_repo.list_by_dataset_and_user(dataset_id, user_id)

    async def get_prediction_download(
        self, prediction_id: UUID, user_id: UUID
    ) -> tuple[str, str]:
        history = await self.pred_repo.get_by_id(prediction_id)
        if not history or history.user_id != user_id:
            raise ResourceNotFoundException("Prediction record not found or access denied")

        if not history.result_file_path or not os.path.exists(history.result_file_path):
            raise ResourceNotFoundException("Prediction result file not found")

        filename = f"predictions_{history.dataset_id}.csv"
        return history.result_file_path, filename
