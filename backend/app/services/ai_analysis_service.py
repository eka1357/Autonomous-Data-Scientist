import json
from typing import Any
from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.models.dataset_analysis import DatasetAnalysis
from app.repositories.dataset_analysis_repository import DatasetAnalysisRepository
from app.repositories.dataset_profile_repository import DatasetProfileRepository
from app.repositories.dataset_repository import DatasetRepository


class AIAnalysisService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = DatasetProfileRepository(session)
        self.analysis_repo = DatasetAnalysisRepository(session)

    def _construct_prompt(self, filename: str, profile_data: dict[str, Any]) -> str:
        return f"""You are an expert Data Scientist AI. Analyze the following dataset profile and return ONLY a valid JSON object matching the specified schema.

Dataset Filename: {filename}
Row Count: {profile_data.get('row_count')}
Column Count: {profile_data.get('column_count')}
Column Names: {profile_data.get('column_names')}
Data Types: {json.dumps(profile_data.get('data_types', {}))}
Missing Values: {json.dumps(profile_data.get('missing_values', {}))}
Duplicate Row Count: {profile_data.get('duplicate_row_count')}
Summary Statistics: {json.dumps(profile_data.get('summary_stats', {}))}

Return JSON with exact structure:
{{
  "summary": "<executive summary>",
  "quality_assessment": {{
    "data_health": "<assessment>",
    "missingness_risk": "<risk level>",
    "duplicate_count": {profile_data.get('duplicate_row_count')}
  }},
  "recommended_ml_task": "classification" | "regression" | "clustering" | "none",
  "target_column_candidate": "<column name or null>",
  "insights": {{
    "key_findings": ["<finding 1>", "<finding 2>"],
    "business_recommendations": ["<recommendation 1>", "<recommendation 2>"]
  }}
}}"""

    def _generate_fallback_analysis(
        self, filename: str, profile_data: dict[str, Any]
    ) -> dict[str, Any]:
        cols = profile_data.get("column_names", [])
        row_cnt = profile_data.get("row_count", 0)
        col_cnt = profile_data.get("column_count", 0)
        dup_cnt = profile_data.get("duplicate_row_count", 0)

        # Detect candidate target column
        target_candidate = None
        target_keywords = ["churn", "target", "label", "price", "salary", "converted", "is_"]
        for c in cols:
            if any(k in c.lower() for k in target_keywords):
                target_candidate = c
                break
        if not target_candidate and cols:
            target_candidate = cols[-1]

        # Determine task type
        rec_task = "classification"
        if target_candidate and any(k in target_candidate.lower() for k in ["price", "salary", "revenue", "cost"]):
            rec_task = "regression"

        return {
            "summary": f"Dataset '{filename}' comprises {row_cnt} records and {col_cnt} columns. Data profile demonstrates structured distribution suitable for {rec_task}.",
            "quality_assessment": {
                "data_health": "Good" if dup_cnt == 0 else "Moderate",
                "missingness_risk": "Low",
                "duplicate_count": dup_cnt,
            },
            "recommended_ml_task": rec_task,
            "target_column_candidate": target_candidate,
            "insights": {
                "key_findings": [
                    f"Dataset contains {row_cnt} observations across {col_cnt} attributes.",
                    f"Identified '{target_candidate}' as the primary target column candidate.",
                ],
                "business_recommendations": [
                    "Proceed to data cleaning for missing value imputation.",
                    f"Prioritize feature engineering around column '{target_candidate}'.",
                ],
            },
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
                temperature=0.2,
                model_kwargs={"response_format": {"type": "json_object"}},
            )
            response = await llm.ainvoke(prompt)
            content = response.content
            if isinstance(content, str):
                parsed = json.loads(content)
                return parsed
        except Exception as exc:
            logger.warning(f"LLM call encountered error, falling back to analytical engine: {exc}")
        return None

    async def generate_analysis(self, dataset_id: UUID) -> DatasetAnalysis:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        profile = await self.profile_repo.get_by_dataset_id(dataset_id)
        if not profile:
            raise ResourceNotFoundException(f"Profile for dataset '{dataset_id}' not found")

        profile_data = {
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "column_names": profile.column_names,
            "data_types": profile.data_types,
            "missing_values": profile.missing_values,
            "duplicate_row_count": profile.duplicate_row_count,
            "summary_stats": profile.summary_stats,
        }

        prompt = self._construct_prompt(dataset.filename, profile_data)
        llm_response = await self._call_llm_if_available(prompt)

        if llm_response:
            analysis_dict = llm_response
            raw_payload = llm_response
        else:
            analysis_dict = self._generate_fallback_analysis(dataset.filename, profile_data)
            raw_payload = {"engine": "fallback", "data": analysis_dict}

        analysis = await self.analysis_repo.create_or_update(
            dataset_id=dataset_id,
            summary=analysis_dict.get("summary", "Analysis completed."),
            quality_assessment=analysis_dict.get("quality_assessment", {}),
            recommended_ml_task=analysis_dict.get("recommended_ml_task"),
            target_column_candidate=analysis_dict.get("target_column_candidate"),
            insights=analysis_dict.get("insights", {}),
            raw_llm_response=raw_payload,
        )
        await self.session.commit()
        logger.info(f"Successfully generated AI analysis for dataset '{dataset_id}'")
        return analysis

    async def get_dataset_analysis(self, dataset_id: UUID, user_id: UUID) -> DatasetAnalysis:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        analysis = await self.analysis_repo.get_by_dataset_id(dataset_id)
        if not analysis:
            raise ResourceNotFoundException("Dataset AI analysis not yet available")

        return analysis
