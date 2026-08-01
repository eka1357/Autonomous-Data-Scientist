from datetime import datetime, timezone
import os
from typing import Any
from uuid import UUID
import joblib
from loguru import logger
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.evaluation_report_generator import generate_html_evaluation_report
from app.core.evaluator import evaluate_trained_model
from app.core.exceptions import ResourceNotFoundException
from app.models.model_evaluation import ModelEvaluation
from app.repositories.dataset_preprocessing_repository import DatasetPreprocessingRepository
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.model_evaluation_repository import ModelEvaluationRepository
from app.repositories.model_training_repository import ModelTrainingRepository


class EvaluationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.prep_repo = DatasetPreprocessingRepository(session)
        self.mt_repo = ModelTrainingRepository(session)
        self.me_repo = ModelEvaluationRepository(session)

    async def run_evaluation(self, dataset_id: UUID) -> ModelEvaluation:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        mt = await self.mt_repo.get_by_dataset_id(dataset_id)
        if not mt or not mt.model_path or not os.path.exists(mt.model_path):
            raise ResourceNotFoundException(f"Trained model for dataset '{dataset_id}' not found")

        prep = await self.prep_repo.get_by_dataset_id(dataset_id)
        if not prep or not prep.x_train_path or not os.path.exists(prep.x_train_path):
            raise ResourceNotFoundException(f"Preprocessed test artifacts for dataset '{dataset_id}' not found")

        # Load joblib model
        try:
            model = joblib.load(mt.model_path)
        except Exception as e:
            raise ValueError(f"Failed to load trained model binary at '{mt.model_path}': {e}")

        # Load X_train, X_test, y_train, y_test
        X_train = pd.read_csv(prep.x_train_path)
        X_test = pd.read_csv(prep.x_test_path) if prep.x_test_path and os.path.exists(prep.x_test_path) else X_train

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

        # Execute Evaluation
        metrics, feature_importance, shap_values = evaluate_trained_model(
            model=model,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            problem_type=mt.problem_type,
        )

        # Render HTML Report
        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        reports_dir = os.path.join(base_dir, "reports", str(dataset_id))
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir, "evaluation_report.html")

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        generate_html_evaluation_report(
            dataset_id=str(dataset_id),
            algorithm=mt.best_algorithm or "Model",
            problem_type=mt.problem_type,
            metrics=metrics,
            feature_importance=feature_importance,
            shap_values=shap_values,
            generated_at=now_str,
            output_report_path=report_path,
        )

        me_record = await self.me_repo.create_or_update(
            dataset_id=dataset_id,
            metrics=metrics,
            feature_importance=feature_importance,
            shap_values=shap_values,
            report_path=report_path,
            status="completed",
        )
        await self.session.commit()
        logger.info(f"Successfully evaluated model for dataset '{dataset_id}' -> {report_path}")
        return me_record

    async def get_evaluation(self, dataset_id: UUID, user_id: UUID) -> ModelEvaluation:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        me = await self.me_repo.get_by_dataset_id(dataset_id)
        if not me:
            raise ResourceNotFoundException("Model evaluation record not found for dataset")

        return me

    async def get_evaluation_report_path(self, dataset_id: UUID, user_id: UUID) -> tuple[str, str]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        me = await self.me_repo.get_by_dataset_id(dataset_id)
        if not me or not me.report_path or not os.path.exists(me.report_path):
            raise ResourceNotFoundException("Model evaluation HTML report not found")

        filename = f"evaluation_report_{dataset.filename}.html"
        return me.report_path, filename
