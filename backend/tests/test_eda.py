import io
import os
import tempfile
import pandas as pd
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.eda_engine import compute_eda_statistics_and_charts
from app.core.report_generator import generate_html_eda_report
from app.services.ai_analysis_service import AIAnalysisService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.profiling_service import ProfilingService


def test_eda_engine_statistics_and_charts() -> None:
    data = {
        "age": [20, 22, 25, 29, 35, 120],  # 120 is an outlier
        "salary": [50000, 55000, 60000, 70000, 85000, 100000],
        "category": ["A", "B", "A", "B", "A", "C"],
    }
    df = pd.DataFrame(data)

    with tempfile.TemporaryDirectory() as tmp_dir:
        stats, corr, outliers, charts = compute_eda_statistics_and_charts(df, "test_dataset", tmp_dir)

        # Basic Stats Check
        assert stats["basic"]["row_count"] == 6
        assert stats["basic"]["column_count"] == 3

        # Numeric Stats Check
        assert "mean" in stats["numeric"]["age"]
        assert "skewness" in stats["numeric"]["age"]

        # IQR Outlier Check (age 120 should be flagged as outlier)
        assert outliers["age"]["outlier_count"] >= 1

        # Chart Generation Check
        assert "hist_age" in charts
        assert "box_age" in charts
        assert "corr_heatmap" in charts
        assert os.path.exists(os.path.join(tmp_dir, charts["hist_age"]))


def test_eda_html_report_generation() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        report_path = os.path.join(tmp_dir, "test_report.html")
        stats = {
            "basic": {"row_count": 10, "column_count": 2, "duplicate_count": 0},
            "numeric": {"age": {"mean": 30, "median": 30, "std": 5, "min": 20, "max": 40, "skewness": 0.1}},
            "categorical": {},
        }
        outliers = {"age": {"q1": 25, "q3": 35, "iqr": 10, "outlier_count": 0, "outlier_percentage": 0.0}}
        insights = {"key_findings": ["Test finding"], "business_recommendations": ["Test recommendation"]}

        res_path = generate_html_eda_report(
            dataset_id="test_id",
            summary="Test Executive Summary",
            statistics=stats,
            outliers=outliers,
            charts={},
            insights=insights,
            generated_at="2026-08-01 12:00:00 UTC",
            output_report_path=report_path,
        )

        assert os.path.exists(res_path)
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "AutoDS — Exploratory Data Analysis Report" in content
            assert "Test Executive Summary" in content


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "EDA User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "EDA Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_eda_service_pipeline_and_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "eda_test@example.com")

    csv_data = b"name,age,salary\nAlice,25,50000\nBob,30,60000\nCharlie,35,70000\nDavid,40,80000\n"
    files = {"file": ("people.csv", io.BytesIO(csv_data), "text/csv")}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id}, files=files, headers=headers
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Execute full pipeline including EDA
    await ProfilingService(db_session).run_profiling(dataset_id)
    await AIAnalysisService(db_session).generate_analysis(dataset_id)
    await CleaningService(db_session).generate_and_execute_cleaning(dataset_id)
    eda_record = await EDAService(db_session).run_eda(dataset_id)

    assert eda_record.summary is not None
    assert "age" in eda_record.statistics["numeric"]

    # 1. Test GET /{dataset_id}/eda
    eda_res = await async_client.get(f"/api/v1/datasets/{dataset_id}/eda", headers=headers)
    assert eda_res.status_code == 200
    assert eda_res.json()["data"]["dataset_id"] == dataset_id
    assert "statistics" in eda_res.json()["data"]
    assert "charts" in eda_res.json()["data"]

    # 2. Test GET /{dataset_id}/eda-report
    report_res = await async_client.get(f"/api/v1/datasets/{dataset_id}/eda-report", headers=headers)
    assert report_res.status_code == 200
    assert "text/html" in report_res.headers["content-type"]
    assert b"Exploratory Data Analysis Report" in report_res.content


@pytest.mark.asyncio
async def test_eda_unauthorized_access(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers_a, project_id_a = await _get_auth_headers_and_project(async_client, "eda_owner_a@example.com")
    headers_b, _ = await _get_auth_headers_and_project(async_client, "eda_owner_b@example.com")

    files = {"file": ("data.csv", io.BytesIO(b"x,y\n1,2\n3,4\n"), "text/csv")}
    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id_a}, files=files, headers=headers_a
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    await ProfilingService(db_session).run_profiling(dataset_id)
    await AIAnalysisService(db_session).generate_analysis(dataset_id)
    await CleaningService(db_session).generate_and_execute_cleaning(dataset_id)
    await EDAService(db_session).run_eda(dataset_id)

    # User B accessing User A's EDA -> 404
    eda_b = await async_client.get(f"/api/v1/datasets/{dataset_id}/eda", headers=headers_b)
    assert eda_b.status_code == 404

    # User B downloading User A's EDA report -> 404
    report_b = await async_client.get(f"/api/v1/datasets/{dataset_id}/eda-report", headers=headers_b)
    assert report_b.status_code == 404
