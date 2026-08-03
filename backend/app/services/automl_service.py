import os
from typing import Any
from uuid import UUID
from loguru import logger
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.automl_engine import detect_problem_type, train_automl_models
from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.models.model_training import ModelTraining
from app.repositories.dataset_preprocessing_repository import DatasetPreprocessingRepository
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.model_training_repository import ModelTrainingRepository


class AutoMLService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.prep_repo = DatasetPreprocessingRepository(session)
        self.mt_repo = ModelTrainingRepository(session)

    async def run_automl(
        self,
        dataset_id: UUID,
        target_column: str | None = None,
        problem_type_override: str | None = None,
    ) -> ModelTraining:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        prep = await self.prep_repo.get_by_dataset_id(dataset_id)
        if not prep or not prep.x_train_path or not os.path.exists(prep.x_train_path):
            raise ResourceNotFoundException(f"Preprocessed dataset artifacts for '{dataset_id}' not found")

        target_col = target_column or prep.target_column

        # Load X_train and X_test
        X_train = pd.read_csv(prep.x_train_path)
        X_test = pd.read_csv(prep.x_test_path) if prep.x_test_path and os.path.exists(prep.x_test_path) else X_train

        # Load y_train and y_test if present
        y_train, y_test = None, None
        if prep.y_train_path and os.path.exists(prep.y_train_path) and os.path.getsize(prep.y_train_path) > 0:
            try:
                y_train_df = pd.read_csv(prep.y_train_path)
                y_train = y_train_df.iloc[:, 0]
            except Exception:
                y_train = None

        if prep.y_test_path and os.path.exists(prep.y_test_path) and os.path.getsize(prep.y_test_path) > 0:
            try:
                y_test_df = pd.read_csv(prep.y_test_path)
                y_test = y_test_df.iloc[:, 0]
            except Exception:
                y_test = None

        # Determine problem type
        dummy_df = X_train.copy()
        if y_train is not None and target_col:
            dummy_df[target_col] = y_train.values

        problem_type, actual_target_col = detect_problem_type(
            dummy_df, target_col=target_col, problem_type_override=problem_type_override
        )

        # Output model path
        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        model_dir = os.path.join(base_dir, "models", str(dataset_id))
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "best_model.joblib")

        # Train models
        best_model_obj, best_algorithm, best_score, primary_metric, leaderboard = train_automl_models(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            problem_type=problem_type,
            model_output_path=model_path,
        )

        mt_record = await self.mt_repo.create_or_update(
            dataset_id=dataset_id,
            problem_type=problem_type,
            target_column=actual_target_col,
            best_algorithm=best_algorithm,
            best_score=best_score,
            primary_metric=primary_metric,
            leaderboard=leaderboard,
            model_path=model_path,
            status="completed",
        )
        await self.session.commit()
        logger.info(
            f"Successfully trained AutoML models for dataset '{dataset_id}'. Best: {best_algorithm} (Score: {best_score})"
        )
        return mt_record

    async def get_model_training(self, dataset_id: UUID, user_id: UUID) -> ModelTraining:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        mt = await self.mt_repo.get_by_dataset_id(dataset_id)
        if not mt:
            raise ResourceNotFoundException("Model training record not found for dataset")

        return mt

    async def get_model_download_path(self, dataset_id: UUID, user_id: UUID, format: str = "joblib") -> tuple[str, str]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        mt = await self.mt_repo.get_by_dataset_id(dataset_id)
        if not mt or not mt.model_path or not os.path.exists(mt.model_path):
            raise ResourceNotFoundException("Trained model binary not found or not yet generated")

        target_path = mt.model_path
        filename = f"{dataset.filename}_best_model.{format}"

        if format == "onnx":
            onnx_path = mt.model_path.replace(".joblib", ".onnx")
            if not os.path.exists(onnx_path):
                raise ResourceNotFoundException("ONNX model binary not found or not yet generated")
            target_path = onnx_path

        return target_path, filename
