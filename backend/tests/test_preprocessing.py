import io
import os
import pandas as pd
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.preprocessor import execute_preprocessing_plan
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.preprocessing_service import PreprocessingService
from app.services.profiling_service import ProfilingService
from app.worker.tasks import preprocess_dataset_task, process_uploaded_dataset


def test_core_preprocessing_engine_all_operations() -> None:
    data = {
        "age": [20, 25, 30, 35, 40, 45, 50, 55, 60, 65],
        "income": [30000.0, 40000.0, 50000.0, 60000.0, 70000.0, 80000.0, 90000.0, 100000.0, 110000.0, 120000.0],
        "city": ["NY", "LA", "NY", "SF", "LA", "NY", "SF", "LA", "NY", "SF"],
        "education": ["BSc", "MSc", "BSc", "PhD", "MSc", "BSc", "PhD", "MSc", "BSc", "PhD"],
        "target": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    }
    df = pd.DataFrame(data)

    plan = {
        "target_column": "target",
        "test_size": 0.2,
        "random_state": 42,
        "encode_categorical": {
            "city": "onehot",
            "education": "ordinal",
        },
        "scale_numeric": {
            "age": "standard",
            "income": "minmax",
        },
        "feature_selection": {"enabled": False},
    }

    ml_df, X_train, X_test, y_train, y_test, summary = execute_preprocessing_plan(df, plan)

    # Basic shape assertions
    assert len(ml_df) == 10
    assert "city_NY" in ml_df.columns or "city_LA" in ml_df.columns
    assert "education" in ml_df.columns
    assert len(X_train) == 8
    assert len(X_test) == 2
    assert y_train is not None and len(y_train) == 8
    assert y_test is not None and len(y_test) == 2
    assert summary["target_column"] == "target"
    assert summary["feature_count"] >= 4


def test_core_preprocessing_scalers_and_encodings() -> None:
    data = {
        "val_robust": [1.0, 2.0, 3.0, 100.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "val_norm": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
        "category_label": ["red", "blue", "green", "red", "blue", "green", "red", "blue", "green", "red"],
        "target": ["yes", "no", "yes", "no", "yes", "no", "yes", "no", "yes", "no"],
    }
    df = pd.DataFrame(data)

    plan = {
        "target_column": "target",
        "test_size": 0.3,
        "random_state": 123,
        "encode_categorical": {"category_label": "label"},
        "scale_numeric": {"val_robust": "robust", "val_norm": "normalize"},
    }

    ml_df, X_train, X_test, y_train, y_test, summary = execute_preprocessing_plan(df, plan)

    assert len(X_train) == 7
    assert len(X_test) == 3
    assert y_train is not None
    assert summary["rows_after"] == 10


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Prep User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Preprocessing Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_preprocessing_service_and_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "prep_test@example.com")

    # Upload dataset
    csv_content = (
        "age,salary,city,label\n"
        "25,50000,NY,0\n"
        "30,60000,LA,1\n"
        "35,70000,NY,0\n"
        "40,80000,SF,1\n"
        "45,90000,LA,0\n"
        "50,100000,NY,1\n"
        "55,110000,SF,0\n"
        "60,120000,LA,1\n"
        "65,130000,NY,0\n"
        "70,140000,SF,1\n"
    )
    files = {"file": ("test_ml.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"project_id": project_id}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload",
        files=files,
        data=data,
        headers=headers,
    )
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["data"]["id"]

    # Run full pipeline through services
    from uuid import UUID
    d_uuid = UUID(dataset_id)
    await ProfilingService(db_session).run_profiling(d_uuid)
    await CleaningService(db_session).generate_and_execute_cleaning(d_uuid)
    await EDAService(db_session).run_eda(d_uuid)

    # Trigger Preprocessing via API Endpoint
    prep_req = {
        "target_column": "label",
        "test_size": 0.2,
        "encode_categorical": {"city": "onehot"},
        "scale_numeric": {"age": "standard", "salary": "minmax"},
    }
    prep_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/preprocess",
        json=prep_req,
        headers=headers,
    )
    assert prep_res.status_code == 200
    prep_data = prep_res.json()["data"]
    assert prep_data["status"] == "completed"
    assert prep_data["ml_ready_path"] is not None

    # Get Preprocessing Status via API
    get_prep_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/preprocessing",
        headers=headers,
    )
    assert get_prep_res.status_code == 200
    assert get_prep_res.json()["data"]["status"] == "completed"

    # Download ML-Ready file via API
    ml_ready_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/ml-ready",
        headers=headers,
    )
    assert ml_ready_res.status_code == 200
    assert "age" in ml_ready_res.text or "label" in ml_ready_res.text

    # Test Celery tasks
    celery_res = preprocess_dataset_task(dataset_id)
    assert celery_res["status"] == "completed"

    pipeline_res = process_uploaded_dataset(dataset_id)
    assert pipeline_res["status"] == "completed"
