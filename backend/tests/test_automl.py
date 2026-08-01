import io
import os
import numpy as np
import pandas as pd
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.automl_engine import detect_problem_type, train_automl_models
from app.services.automl_service import AutoMLService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.preprocessing_service import PreprocessingService
from app.services.profiling_service import ProfilingService
from app.worker.tasks import train_models_task


def test_problem_type_detection() -> None:
    df_cls = pd.DataFrame({"feat1": [1, 2, 3], "target": [0, 1, 0]})
    p_type, t_col = detect_problem_type(df_cls, "target")
    assert p_type == "classification"

    df_reg = pd.DataFrame({"feat1": range(20), "target": [float(i * 1.5) for i in range(20)]})
    p_type_reg, _ = detect_problem_type(df_reg, "target")
    assert p_type_reg == "regression"

    df_cluster = pd.DataFrame({"feat1": [1, 2, 3], "feat2": [4, 5, 6]})
    p_type_cl, _ = detect_problem_type(df_cluster, None)
    assert p_type_cl == "clustering"


def test_automl_classification_training() -> None:
    X_train = pd.DataFrame({"f1": np.random.randn(50), "f2": np.random.randn(50)})
    X_test = pd.DataFrame({"f1": np.random.randn(20), "f2": np.random.randn(20)})
    y_train = pd.Series(np.random.choice([0, 1], size=50))
    y_test = pd.Series(np.random.choice([0, 1], size=20))

    best_obj, best_name, best_score, primary_metric, leaderboard = train_automl_models(
        X_train, X_test, y_train, y_test, problem_type="classification"
    )

    assert best_obj is not None
    assert primary_metric == "f1_weighted"
    assert len(leaderboard) >= 3
    assert any(item["algorithm"] == "Logistic Regression" for item in leaderboard)
    assert any(item["algorithm"] == "Random Forest" for item in leaderboard)


def test_automl_regression_training() -> None:
    X_train = pd.DataFrame({"f1": np.random.randn(50), "f2": np.random.randn(50)})
    X_test = pd.DataFrame({"f1": np.random.randn(20), "f2": np.random.randn(20)})
    y_train = pd.Series(np.random.randn(50))
    y_test = pd.Series(np.random.randn(20))

    best_obj, best_name, best_score, primary_metric, leaderboard = train_automl_models(
        X_train, X_test, y_train, y_test, problem_type="regression"
    )

    assert best_obj is not None
    assert primary_metric == "r2"
    assert len(leaderboard) >= 3
    assert any("Linear Regression" in item["algorithm"] for item in leaderboard)


def test_automl_clustering_training() -> None:
    X_train = pd.DataFrame({"f1": np.random.randn(30), "f2": np.random.randn(30)})
    X_test = pd.DataFrame({"f1": np.random.randn(10), "f2": np.random.randn(10)})

    best_obj, best_name, best_score, primary_metric, leaderboard = train_automl_models(
        X_train, X_test, problem_type="clustering"
    )

    assert best_obj is not None
    assert primary_metric == "silhouette_score"
    assert len(leaderboard) >= 3
    assert any(item["algorithm"] == "KMeans" for item in leaderboard)


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "AutoML User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "AutoML Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_automl_service_and_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "automl_test@example.com")

    # Upload dataset
    csv_content = (
        "feature1,feature2,category,target\n"
        "1.0,2.0,A,0\n"
        "2.0,3.0,B,1\n"
        "3.0,4.0,A,0\n"
        "4.0,5.0,C,1\n"
        "5.0,6.0,B,0\n"
        "6.0,7.0,A,1\n"
        "7.0,8.0,C,0\n"
        "8.0,9.0,B,1\n"
        "9.0,10.0,A,0\n"
        "10.0,11.0,C,1\n"
    )
    files = {"file": ("automl_ds.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"project_id": project_id}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload",
        files=files,
        data=data,
        headers=headers,
    )
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["data"]["id"]

    # Run precursor services
    from uuid import UUID
    d_uuid = UUID(dataset_id)
    await ProfilingService(db_session).run_profiling(d_uuid)
    await CleaningService(db_session).generate_and_execute_cleaning(d_uuid)
    await EDAService(db_session).run_eda(d_uuid)
    await PreprocessingService(db_session).run_preprocessing(d_uuid, target_column="target")

    # Trigger AutoML via API
    train_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/automl",
        json={"target_column": "target"},
        headers=headers,
    )
    assert train_res.status_code == 200
    res_data = train_res.json()["data"]
    assert res_data["status"] == "completed"
    assert res_data["best_algorithm"] is not None
    assert len(res_data["leaderboard"]) > 0

    # Get models summary
    get_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/models",
        headers=headers,
    )
    assert get_res.status_code == 200
    assert get_res.json()["data"]["status"] == "completed"

    # Download model binary
    dl_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/models/download",
        headers=headers,
    )
    assert dl_res.status_code == 200

    # Test Celery task
    c_res = train_models_task(dataset_id)
    assert c_res["status"] == "completed"
