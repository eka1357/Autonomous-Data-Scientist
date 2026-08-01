import json
import os
from typing import Any
from uuid import UUID
from loguru import logger
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.core.preprocessor import execute_preprocessing_plan
from app.repositories.dataset_analysis_repository import DatasetAnalysisRepository
from app.repositories.dataset_profile_repository import DatasetProfileRepository
from app.repositories.dataset_repository import DatasetRepository


class PreprocessingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = DatasetProfileRepository(session)
        self.analysis_repo = DatasetAnalysisRepository(session)

    def _generate_default_preprocessing_plan(
        self, profile_data: dict[str, Any]
    ) -> dict[str, Any]:
        data_types = profile_data.get("data_types", {})

        encode_cat: dict[str, str] = {}
        for col, dtype in data_types.items():
            if any(k in str(dtype).lower() for k in ["object", "string", "category"]):
                encode_cat[col] = "label"

        scale_num: dict[str, str] = {}
        for col, dtype in data_types.items():
            if any(k in str(dtype).lower() for k in ["int", "float"]):
                scale_num[col] = "standard"

        return {
            "encode_categorical": encode_cat,
            "scale_numeric": scale_num,
        }

    async def execute_ml_preprocessing(
        self, dataset_id: UUID, custom_plan: dict[str, Any] | None = None
    ) -> tuple[str, dict[str, Any]]:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        # Must use cleaned.csv as source input
        source_path = dataset.cleaned_storage_path or dataset.raw_storage_path
        if not source_path or not os.path.exists(source_path):
            raise ResourceNotFoundException(f"Source data file '{source_path}' not found")

        profile = await self.profile_repo.get_by_dataset_id(dataset_id)
        profile_data = {
            "data_types": profile.data_types if profile else {},
            "column_names": profile.column_names if profile else [],
        }

        plan = custom_plan or self._generate_default_preprocessing_plan(profile_data)

        # Read cleaned dataset
        df = None
        for enc in ["utf-8", "latin-1", "utf-8-sig"]:
            try:
                df = pd.read_csv(source_path, encoding=enc)
                break
            except Exception:
                continue

        if df is None:
            raise ValueError(f"Failed to read dataset file '{source_path}'")

        # Execute ML Preprocessing (Encoding & Scaling)
        ml_ready_df, summary = execute_preprocessing_plan(df, plan)

        # Save ml_ready.csv
        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        preprocessed_dir = os.path.join(base_dir, "preprocessed")
        os.makedirs(preprocessed_dir, exist_ok=True)

        ml_ready_filename = f"{dataset_id}_ml_ready.csv"
        ml_ready_path = os.path.join(preprocessed_dir, ml_ready_filename)
        ml_ready_df.to_csv(ml_ready_path, index=False)

        logger.info(f"Successfully generated ML-ready dataset for '{dataset_id}' -> {ml_ready_path}")
        return ml_ready_path, summary
