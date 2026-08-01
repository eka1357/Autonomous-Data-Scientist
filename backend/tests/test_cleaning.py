import io
import pandas as pd
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cleaner import execute_cleaning_plan
from app.services.ai_analysis_service import AIAnalysisService
from app.services.cleaning_service import CleaningService
from app.services.profiling_service import ProfilingService


from app.core.preprocessor import execute_preprocessing_plan


def test_pandas_cleaner_engine_operations() -> None:
    data = {
        "name": [" Alice ", "Bob", " Alice ", "Charlie", None],
        "age": [25.0, 30.0, 25.0, None, 40.0],
        "salary": [50000.0, 60000.0, 50000.0, 70000.0, 80000.0],
    }
    df = pd.DataFrame(data)

    cleaning_plan = {
        "remove_duplicates": True,
        "trim_whitespace": True,
        "fill_missing": {"age": "median", "name": "mode"},
    }

    cleaned_df, summary = execute_cleaning_plan(df, cleaning_plan)

    # Human readable checks: string names preserved, not converted to integers/floats
    assert summary["rows_after"] < summary["rows_before"]
    assert cleaned_df["name"].iloc[0] == "Alice"  # Trimmed whitespace
    assert cleaned_df["age"].isna().sum() == 0
    assert cleaned_df["name"].isna().sum() == 0
    assert cleaned_df["salary"].iloc[0] == 50000.0  # Not scaled


def test_pandas_preprocessor_engine_operations() -> None:
    data = {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25.0, 30.0, 40.0],
        "salary": [50000.0, 60000.0, 80000.0],
    }
    df = pd.DataFrame(data)

    preprocessing_plan = {
        "encode_categorical": {"name": "label"},
        "scale_numeric": {"salary": "minmax"},
    }

    ml_df, summary = execute_preprocessing_plan(df, preprocessing_plan)

    # ML Ready checks: numeric label encoding & minmax scaling applied
    assert pd.api.types.is_numeric_dtype(ml_df["name"])
    assert ml_df["salary"].min() == 0.0
    assert ml_df["salary"].max() == 1.0



async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Cleaning User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Cleaning Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_cleaning_service_pipeline_and_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "clean_test@example.com")

    csv_data = b"name,age,salary\nAlice,25,50000\nBob,,60000\nAlice,25,50000\n"
    files = {"file": ("staff.csv", io.BytesIO(csv_data), "text/csv")}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id}, files=files, headers=headers
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Execute full pipeline steps
    await ProfilingService(db_session).run_profiling(dataset_id)
    await AIAnalysisService(db_session).generate_analysis(dataset_id)

    cleaning_service = CleaningService(db_session)
    cleaning_record = await cleaning_service.generate_and_execute_cleaning(dataset_id)
    assert cleaning_record.status == "completed"

    # 1. Test GET /{dataset_id}/cleaning-plan
    plan_res = await async_client.get(f"/api/v1/datasets/{dataset_id}/cleaning-plan", headers=headers)
    assert plan_res.status_code == 200
    original_plan = plan_res.json()["data"]["cleaning_plan"]
    assert plan_res.json()["data"]["status"] == "completed"

    # 2. Test POST /{dataset_id}/clean (NO request body)
    clean_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/clean",
        headers=headers,
    )
    assert clean_res.status_code == 200
    # Verify stored plan remains identical (not overwritten)
    assert clean_res.json()["data"]["cleaning_plan"] == original_plan
    assert clean_res.json()["data"]["status"] == "completed"

    # 3. Test GET /{dataset_id}/cleaned-file
    file_res = await async_client.get(f"/api/v1/datasets/{dataset_id}/cleaned-file", headers=headers)
    assert file_res.status_code == 200
    assert "text/csv" in file_res.headers["content-type"]
    assert b"name,age,salary" in file_res.content


@pytest.mark.asyncio
async def test_clean_endpoint_404_when_no_cleaning_plan_exists(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "clean_404_test@example.com")

    csv_data = b"x,y\n1,2\n"
    files = {"file": ("data.csv", io.BytesIO(csv_data), "text/csv")}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id}, files=files, headers=headers
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Calling POST /clean without running generate_and_execute_cleaning first -> 404
    clean_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/clean",
        headers=headers,
    )
    assert clean_res.status_code == 404
    assert "Cleaning plan not found" in clean_res.json()["error"]["message"]


@pytest.mark.asyncio
async def test_cleaning_unauthorized_access(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers_a, project_id_a = await _get_auth_headers_and_project(async_client, "clean_owner_a@example.com")
    headers_b, _ = await _get_auth_headers_and_project(async_client, "clean_owner_b@example.com")

    files = {"file": ("data.csv", io.BytesIO(b"x,y\n1,2\n"), "text/csv")}
    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id_a}, files=files, headers=headers_a
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    await ProfilingService(db_session).run_profiling(dataset_id)
    await AIAnalysisService(db_session).generate_analysis(dataset_id)
    await CleaningService(db_session).generate_and_execute_cleaning(dataset_id)

    # Owner B attempts to access Owner A's cleaning plan -> 404
    plan_b = await async_client.get(f"/api/v1/datasets/{dataset_id}/cleaning-plan", headers=headers_b)
    assert plan_b.status_code == 404

    # Owner B attempts to download Owner A's cleaned file -> 404
    file_b = await async_client.get(f"/api/v1/datasets/{dataset_id}/cleaned-file", headers=headers_b)
    assert file_b.status_code == 404

