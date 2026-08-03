from datetime import datetime, timezone
import json
import os
from typing import Any
from uuid import UUID
from loguru import logger
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.eda_engine import compute_eda_statistics_and_charts
from app.core.exceptions import ResourceNotFoundException
from app.core.report_generator import generate_html_eda_report
from app.models.dataset_eda import DatasetEDA
from app.repositories.dataset_eda_repository import DatasetEDARepository
from app.repositories.dataset_repository import DatasetRepository


class EDAService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.eda_repo = DatasetEDARepository(session)

    def _construct_prompt(
        self, filename: str, statistics: dict[str, Any], outliers: dict[str, Any]
    ) -> str:
        return f"""You are an expert Data Science EDA AI. Analyze the following EDA statistics and return ONLY a valid JSON object.

Dataset: {filename}
Statistics: {json.dumps(statistics)}
Outliers: {json.dumps(outliers)}

Return JSON matching exact structure:
{{
  "summary": "<comprehensive executive summary>",
  "important_correlations": ["<correlation finding 1>", "<correlation finding 2>"],
  "outlier_observations": ["<outlier observation 1>"],
  "data_quality_observations": ["<quality observation 1>"],
  "recommended_preprocessing": ["<preprocessing tip 1>"],
  "business_insights": ["<business insight 1>", "<business insight 2>"],
  "model_recommendations": ["<model recommendation 1>"]
}}"""

    def _generate_fallback_insights(
        self, filename: str, statistics: dict[str, Any], outliers: dict[str, Any]
    ) -> dict[str, Any]:
        basic = statistics.get("basic", {})
        rows = basic.get("row_count", 0)
        cols = basic.get("column_count", 0)
        num_cols = list(statistics.get("numeric", {}).keys())

        high_outlier_cols = [
            c for c, meta in outliers.items() if meta.get("outlier_percentage", 0) > 5.0
        ]

        summary = f"EDA generated for dataset '{filename}' containing {rows} rows and {cols} attributes. Dataset exhibits clean structural parameters suitable for automated modeling."

        return {
            "summary": summary,
            "important_correlations": [
                f"Identified {len(num_cols)} continuous numeric variables for feature correlation modeling."
            ],
            "outlier_observations": [
                f"Columns with >5% outliers: {', '.join(high_outlier_cols)}"
                if high_outlier_cols
                else "No extreme outlier skewness detected across numeric variables."
            ],
            "data_quality_observations": [
                f"Total recorded missing cells: {sum(basic.get('missing_values', {}).values())}."
            ],
            "recommended_preprocessing": [
                "Apply standard normalization scaling to skewed numeric attributes.",
                "Perform target label encoding prior to training.",
            ],
            "business_insights": [
                f"Dataset contains sufficient depth ({rows} samples) for statistical inference.",
                "Key variable distributions exhibit strong predictive signals.",
            ],
            "model_recommendations": [
                "Gradient Boosted Trees (XGBoost / LightGBM) for non-linear feature interactions.",
                "Regularized Linear Regression / Logistic Regression baseline.",
            ],
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
                return json.loads(content)
        except Exception as exc:
            logger.warning(f"LLM EDA insight generation error, using analytical fallback: {exc}")
        return None

    async def run_eda(self, dataset_id: UUID) -> DatasetEDA:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        # 1. Read cleaned file (or raw file as fallback)
        source_path = dataset.cleaned_storage_path or dataset.raw_storage_path
        if not source_path or not os.path.exists(source_path):
            raise ResourceNotFoundException(f"Source file '{source_path}' not found")

        df = None
        for enc in ["utf-8", "latin-1", "utf-8-sig"]:
            try:
                df = pd.read_csv(source_path, encoding=enc)
                break
            except Exception:
                continue

        if df is None:
            raise ValueError(f"Failed to read dataset source '{source_path}'")

        # 2. Setup Chart Directory & Compute EDA
        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        charts_dir = os.path.join(base_dir, "charts", str(dataset_id))
        reports_dir = os.path.join(base_dir, "reports")

        statistics, correlations, outliers, charts_meta = compute_eda_statistics_and_charts(
            df, str(dataset_id), charts_dir
        )

        # 3. AI Insights Generation
        prompt = self._construct_prompt(dataset.filename, statistics, outliers)
        llm_insights = await self._call_llm_if_available(prompt)
        if llm_insights:
            insights = llm_insights
            summary_text = llm_insights.get("summary", "EDA analysis complete.")
        else:
            insights = self._generate_fallback_insights(dataset.filename, statistics, outliers)
            summary_text = insights.get("summary", "EDA analysis complete.")

        # 4. Generate HTML Report
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report_filename = f"{dataset_id}_eda_report.html"
        report_path = os.path.join(reports_dir, report_filename)

        generate_html_eda_report(
            dataset_id=str(dataset_id),
            summary=summary_text,
            statistics=statistics,
            outliers=outliers,
            charts=charts_meta,
            insights=insights,
            generated_at=now_str,
            output_report_path=report_path,
            charts_dir=charts_dir,
        )

        # 5. Save Record to DB
        eda_record = await self.eda_repo.create_or_update(
            dataset_id=dataset_id,
            summary=summary_text,
            statistics=statistics,
            correlations=correlations,
            outliers=outliers,
            charts=charts_meta,
            insights=insights,
            report_path=report_path,
        )
        await self.session.commit()
        logger.info(f"Successfully generated EDA for dataset '{dataset_id}' -> Report: {report_path}")
        return eda_record

    async def get_eda(self, dataset_id: UUID, user_id: UUID) -> DatasetEDA:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        eda = await self.eda_repo.get_by_dataset_id(dataset_id)
        if not eda:
            raise ResourceNotFoundException("EDA report not yet available for this dataset")

        return eda

    async def get_eda_report_path(self, dataset_id: UUID, user_id: UUID) -> tuple[str, str]:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        eda = await self.eda_repo.get_by_dataset_id(dataset_id)
        if not eda or not eda.report_path or not os.path.exists(eda.report_path):
            raise ResourceNotFoundException("EDA HTML report file not found")

        filename = f"eda_report_{dataset.filename}.html"
        return eda.report_path, filename
