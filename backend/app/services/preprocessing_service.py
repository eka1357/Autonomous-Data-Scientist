import os
from typing import Any
from uuid import UUID
from loguru import logger
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.core.preprocessor import execute_preprocessing_plan
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.repositories.dataset_analysis_repository import DatasetAnalysisRepository
from app.repositories.dataset_preprocessing_repository import DatasetPreprocessingRepository
from app.repositories.dataset_repository import DatasetRepository


class PreprocessingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.analysis_repo = DatasetAnalysisRepository(session)
        self.prep_repo = DatasetPreprocessingRepository(session)

    def _generate_default_plan(
        self, df: pd.DataFrame, target_column: str | None = None
    ) -> dict[str, Any]:
        if not target_column or target_column not in df.columns:
            target_column = df.columns[-1] if len(df.columns) > 0 else None

        encode_cat: dict[str, str] = {}
        scale_num: dict[str, str] = {}

        for col in df.columns:
            if col == target_column:
                continue
            if pd.api.types.is_numeric_dtype(df[col]):
                scale_num[col] = "standard"
            else:
                unique_cnt = df[col].nunique()
                if unique_cnt <= 10:
                    encode_cat[col] = "onehot"
                else:
                    encode_cat[col] = "label"

        return {
            "target_column": target_column,
            "test_size": 0.2,
            "random_state": 42,
            "encode_categorical": encode_cat,
            "scale_numeric": scale_num,
            "feature_selection": {"enabled": False, "threshold": 0.0},
        }

    async def run_preprocessing(
        self,
        dataset_id: UUID,
        custom_plan: dict[str, Any] | None = None,
        target_column: str | None = None,
    ) -> DatasetPreprocessing:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        # Select source dataset file: prefer cleaned_storage_path, fallback to raw_storage_path
        source_path = dataset.cleaned_storage_path
        if not source_path or not os.path.exists(source_path):
            source_path = dataset.raw_storage_path

        if not source_path or not os.path.exists(source_path):
            raise ResourceNotFoundException(f"Dataset storage file for '{dataset_id}' not found")

        df = None
        for enc in ["utf-8", "latin-1", "utf-8-sig"]:
            try:
                df = pd.read_csv(source_path, encoding=enc)
                break
            except Exception:
                continue

        if df is None:
            raise ValueError(f"Failed to read source dataset at '{source_path}'")

        # Determine target column candidate from analysis if not supplied
        if not target_column:
            analysis = await self.analysis_repo.get_by_dataset_id(dataset_id)
            if analysis and analysis.target_column_candidate in df.columns:
                target_column = analysis.target_column_candidate

        # Determine plan
        if custom_plan:
            plan = custom_plan
            if target_column and "target_column" not in plan:
                plan["target_column"] = target_column
        else:
            plan = self._generate_default_plan(df, target_column=target_column)

        actual_target_col = plan.get("target_column")

        # Execute preprocessing
        ml_df, X_train, X_test, y_train, y_test, summary = execute_preprocessing_plan(df, plan)

        # Save artifacts to storage
        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        prep_dir = os.path.join(base_dir, "preprocessed", str(dataset_id))
        os.makedirs(prep_dir, exist_ok=True)

        ml_ready_path = os.path.join(prep_dir, "ml_ready.csv")
        x_train_path = os.path.join(prep_dir, "X_train.csv")
        x_test_path = os.path.join(prep_dir, "X_test.csv")
        y_train_path = os.path.join(prep_dir, "y_train.csv")
        y_test_path = os.path.join(prep_dir, "y_test.csv")

        ml_df.to_csv(ml_ready_path, index=False)
        X_train.to_csv(x_train_path, index=False)
        X_test.to_csv(x_test_path, index=False)

        if y_train is not None:
            pd.DataFrame(y_train).to_csv(y_train_path, index=False)
        else:
            y_train_path = ""

        if y_test is not None:
            pd.DataFrame(y_test).to_csv(y_test_path, index=False)
        else:
            y_test_path = ""

        prep_record = await self.prep_repo.create_or_update(
            dataset_id=dataset_id,
            target_column=actual_target_col,
            preprocessing_plan=plan,
            execution_summary=summary,
            status="completed",
            ml_ready_path=ml_ready_path,
            x_train_path=x_train_path,
            x_test_path=x_test_path,
            y_train_path=y_train_path or None,
            y_test_path=y_test_path or None,
        )
        await self.session.commit()
        logger.info(f"Successfully preprocessed dataset '{dataset_id}' -> {prep_dir}")
        return prep_record

    async def get_preprocessing(self, dataset_id: UUID, user_id: UUID) -> DatasetPreprocessing:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        prep = await self.prep_repo.get_by_dataset_id(dataset_id)
        if not prep:
            raise ResourceNotFoundException("Preprocessing record not found for dataset")

        return prep

    async def get_ml_ready_file(self, dataset_id: UUID, user_id: UUID) -> tuple[str, str]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        prep = await self.prep_repo.get_by_dataset_id(dataset_id)
        if not prep or not prep.ml_ready_path or not os.path.exists(prep.ml_ready_path):
            raise ResourceNotFoundException("ML-ready dataset not found or not yet generated")

        filename = f"ml_ready_{dataset.filename}"
        return prep.ml_ready_path, filename
