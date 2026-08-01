import json
import os
from typing import Any
from uuid import UUID
from loguru import logger
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cleaner import execute_cleaning_plan
from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.models.dataset_cleaning import DatasetCleaning
from app.repositories.dataset_analysis_repository import DatasetAnalysisRepository
from app.repositories.dataset_cleaning_repository import DatasetCleaningRepository
from app.repositories.dataset_profile_repository import DatasetProfileRepository
from app.repositories.dataset_repository import DatasetRepository


class CleaningService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = DatasetProfileRepository(session)
        self.analysis_repo = DatasetAnalysisRepository(session)
        self.cleaning_repo = DatasetCleaningRepository(session)

    def _construct_prompt(
        self,
        filename: str,
        profile_data: dict[str, Any],
        analysis_data: dict[str, Any] | None,
    ) -> str:
        return f"""You are an expert Data Cleaning AI. Generate a structured JSON data cleaning plan based on the dataset profile and AI analysis below.
Do NOT include ML preprocessing, categorical encoding (label/one-hot encoding), scaling, or normalization in this cleaning plan. Focus strictly on data cleaning operations that maintain human-readable text and numbers.

Dataset: {filename}
Profile: {json.dumps(profile_data)}
Analysis: {json.dumps(analysis_data or {})}

Return ONLY a valid JSON object matching this exact schema:
{{
  "remove_duplicates": true,
  "trim_whitespace": true,
  "drop_columns": ["<unwanted column 1>"],
  "fill_missing": {{
    "<column_name>": "mean" | "median" | "mode" | "drop" | "ffill" | "bfill" | "<constant_value>"
  }}
}}"""

    def _generate_fallback_cleaning_plan(
        self, profile_data: dict[str, Any]
    ) -> dict[str, Any]:
        data_types = profile_data.get("data_types", {})
        missing_vals = profile_data.get("missing_values", {})
        dup_cnt = profile_data.get("duplicate_row_count", 0)

        fill_missing: dict[str, str] = {}
        for col, missing_count in missing_vals.items():
            if missing_count > 0:
                dtype = data_types.get(col, "")
                if "int" in dtype or "float" in dtype:
                    fill_missing[col] = "median"
                else:
                    fill_missing[col] = "mode"

        return {
            "remove_duplicates": dup_cnt > 0,
            "trim_whitespace": True,
            "drop_columns": [],
            "fill_missing": fill_missing,
        }


    async def _call_llm_if_available(self, prompt: str) -> dict[str, Any] | None:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("your-"):
            return None

        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="openai/gpt-4o-mini",
                api_key=settings.OPENAI_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.1,
                model_kwargs={"response_format": {"type": "json_object"}},
            )
            response = await llm.ainvoke(prompt)
            content = response.content
            if isinstance(content, str):
                return json.loads(content)
        except Exception as exc:
            logger.warning(f"LLM cleaning plan generation error, falling back: {exc}")
        return None

    async def generate_and_execute_cleaning(
        self, dataset_id: UUID, custom_plan: dict[str, Any] | None = None
    ) -> DatasetCleaning:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        profile = await self.profile_repo.get_by_dataset_id(dataset_id)
        analysis = await self.analysis_repo.get_by_dataset_id(dataset_id)

        profile_data = {
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "column_names": profile.column_names if profile else [],
            "data_types": profile.data_types if profile else {},
            "missing_values": profile.missing_values if profile else {},
            "duplicate_row_count": profile.duplicate_row_count if profile else 0,
        }
        analysis_data = (
            {
                "summary": analysis.summary,
                "recommended_ml_task": analysis.recommended_ml_task,
                "target_column_candidate": analysis.target_column_candidate,
            }
            if analysis
            else None
        )

        # 1. Determine cleaning plan
        if custom_plan:
            plan = custom_plan
        else:
            prompt = self._construct_prompt(dataset.filename, profile_data, analysis_data)
            llm_plan = await self._call_llm_if_available(prompt)
            if llm_plan:
                plan = llm_plan
            else:
                plan = self._generate_fallback_cleaning_plan(profile_data)

        # 2. Read raw CSV & Execute Cleaning
        if not os.path.exists(dataset.raw_storage_path):
            raise ResourceNotFoundException(f"Raw storage file '{dataset.raw_storage_path}' not found")

        # Encoding fallback
        df = None
        for enc in ["utf-8", "latin-1", "utf-8-sig"]:
            try:
                df = pd.read_csv(dataset.raw_storage_path, encoding=enc)
                break
            except Exception:
                continue

        if df is None:
            raise ValueError(f"Failed to read dataset file '{dataset.raw_storage_path}'")

        cleaned_df, exec_summary = execute_cleaning_plan(df, plan)

        # 3. Save Cleaned Dataset
        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        cleaned_dir = os.path.join(base_dir, "cleaned")
        os.makedirs(cleaned_dir, exist_ok=True)

        cleaned_filename = f"{dataset_id}_cleaned.csv"
        cleaned_path = os.path.join(cleaned_dir, cleaned_filename)
        cleaned_df.to_csv(cleaned_path, index=False)

        dataset.cleaned_storage_path = cleaned_path

        # 4. Update Database Records
        cleaning_record = await self.cleaning_repo.create_or_update(
            dataset_id=dataset_id,
            cleaning_plan=plan,
            execution_summary=exec_summary,
            status="completed",
        )
        await self.session.commit()
        logger.info(f"Successfully cleaned dataset '{dataset_id}' -> {cleaned_path}")
        return cleaning_record

    async def get_cleaning_plan(self, dataset_id: UUID, user_id: UUID) -> DatasetCleaning:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        cleaning = await self.cleaning_repo.get_by_dataset_id(dataset_id)
        if not cleaning:
            raise ResourceNotFoundException("Dataset cleaning record not yet available")

        return cleaning

    async def get_cleaned_file_path(self, dataset_id: UUID, user_id: UUID) -> tuple[str, str]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        if not dataset.cleaned_storage_path or not os.path.exists(dataset.cleaned_storage_path):
            raise ResourceNotFoundException("Cleaned dataset file not found or not yet generated")

        filename = f"cleaned_{dataset.filename}"
        return dataset.cleaned_storage_path, filename

    async def execute_stored_cleaning_plan(
        self, dataset_id: UUID, user_id: UUID
    ) -> DatasetCleaning:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        cleaning_record = await self.cleaning_repo.get_by_dataset_id(dataset_id)
        if not cleaning_record or not cleaning_record.cleaning_plan:
            raise ResourceNotFoundException(f"Cleaning plan not found for dataset '{dataset_id}'")

        if not os.path.exists(dataset.raw_storage_path):
            raise ResourceNotFoundException(f"Raw storage file '{dataset.raw_storage_path}' not found")

        df = None
        for enc in ["utf-8", "latin-1", "utf-8-sig"]:
            try:
                df = pd.read_csv(dataset.raw_storage_path, encoding=enc)
                break
            except Exception:
                continue

        if df is None:
            raise ValueError(f"Failed to read dataset file '{dataset.raw_storage_path}'")

        cleaned_df, exec_summary = execute_cleaning_plan(df, cleaning_record.cleaning_plan)

        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        cleaned_dir = os.path.join(base_dir, "cleaned")
        os.makedirs(cleaned_dir, exist_ok=True)

        cleaned_filename = f"{dataset_id}_cleaned.csv"
        cleaned_path = os.path.join(cleaned_dir, cleaned_filename)
        cleaned_df.to_csv(cleaned_path, index=False)

        dataset.cleaned_storage_path = cleaned_path

        cleaning_record.execution_summary = exec_summary
        cleaning_record.status = "completed"
        await self.session.commit()
        logger.info(f"Successfully executed stored cleaning plan for dataset '{dataset_id}' -> {cleaned_path}")
        return cleaning_record

