import io
import os
import tempfile
import numpy as np
import pandas as pd
import pytest
from httpx import AsyncClient
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.evaluation_report_generator import generate_html_evaluation_report
from app.core.evaluator import evaluate_trained_model
from app.services.automl_service import AutoMLService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.evaluation_service import EvaluationService
from app.services.preprocessing_service import PreprocessingService
from app.services.profiling_service import ProfilingService
from app.worker.tasks import evaluate_model_task


def test_core_evaluator_classification() -> None:
    X_train = pd.DataFrame({"f1": np.random.randn(50), "f2": np.random.randn(50)})
    X_test = pd.DataFrame({"f1": np.random.randn(20), "f2": np.random.randn(20)})
    y_train = pd.Series(np.random.choice([0, 1], size=50))
    y_test = pd.Series(np.random.choice([0, 1], size=20))

    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X_train, y_train)

    metrics, feat_imp, shap_vals = evaluate_trained_model(
        clf, X_train, X_test, y_train, y_test, problem_type="classification"
    )

    assert "accuracy" in metrics
    assert "f1" in metrics
    assert "confusion_matrix" in metrics
    assert "cross_validation" in metrics
    assert "f1" in metrics
    assert "f1_weighted" not in metrics  # Key is "f1"
    assert "f1" in metrics
    assert len(feat_imp) == 2


def test_core_evaluator_regression() -> None:
    X_train = pd.DataFrame({"f1": np.random.randn(50), "f2": np.random.randn(50)})
    X_test = pd.DataFrame({"f1": np.random.randn(20), "f2": np.random.randn(20)})
    y_train = pd.Series(np.random.randn(50))
    y_test = pd.Series(np.random.randn(20))

    reg = RandomForestRegressor(n_estimators=10, random_state=42)
    reg.fit(X_train, y_train)

    metrics, feat_imp, shap_vals = evaluate_trained_model(
        reg, X_train, X_test, y_train, y_test, problem_type="regression"
    )

    assert "r2" in metrics
    assert "mae" in metrics
    assert "rmse" in metrics
    assert "cross_validation" in metrics


def test_evaluation_html_report_generation() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        report_path = os.path.join(tmp_dir, "eval_report.html")
        metrics = {"accuracy": 0.95, "f1": 0.94, "cross_validation": {"mean": 0.93, "std": 0.01, "folds": [0.92, 0.94]}}
        feat_imp = {"f1": 0.6, "f2": 0.4}
        shap_vals = {"f1": 0.55, "f2": 0.35}

        res = generate_html_evaluation_report(
            dataset_id="test_id",
            algorithm="Random Forest",
            problem_type="classification",
            metrics=metrics,
            feature_importance=feat_imp,
            shap_values=shap_vals,
            generated_at="2026-08-01 12:00:00 UTC",
            output_report_path=report_path,
        )

        assert os.path.exists(res)
        with open(res, "r", encoding="utf-8") as f:
            content = f.read()
            assert "AutoDS — Model Evaluation Report" in content
            assert "Random Forest" in content


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Eval User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Eval Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_evaluation_service_and_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "eval_test@example.com")

    # Upload dataset
    csv_content = (
        "f1,f2,target\n"
        "1.0,2.0,0\n"
        "2.0,3.0,1\n"
        "3.0,4.0,0\n"
        "4.0,5.0,1\n"
        "5.0,6.0,0\n"
        "6.0,7.0,1\n"
        "7.0,8.0,0\n"
        "8.0,9.0,1\n"
        "9.0,10.0,0\n"
        "10.0,11.0,1\n"
    )
    files = {"file": ("eval_ds.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"project_id": project_id}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload",
        files=files,
        data=data,
        headers=headers,
    )
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["data"]["id"]

    # Run precursor pipeline steps
    from uuid import UUID
    d_uuid = UUID(dataset_id)
    await ProfilingService(db_session).run_profiling(d_uuid)
    await CleaningService(db_session).generate_and_execute_cleaning(d_uuid)
    await EDAService(db_session).run_eda(d_uuid)
    await PreprocessingService(db_session).run_preprocessing(d_uuid, target_column="target")
    await AutoMLService(db_session).run_automl(d_uuid, target_column="target")

    # Trigger Evaluation via API
    eval_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/evaluate",
        headers=headers,
    )
    assert eval_res.status_code == 200
    res_data = eval_res.json()["data"]
    assert res_data["status"] == "completed"
    assert "accuracy" in res_data["metrics"] or "r2" in res_data["metrics"] or "cluster_count" in res_data["metrics"]

    # Get evaluation results
    get_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/evaluation",
        headers=headers,
    )
    assert get_res.status_code == 200
    assert get_res.json()["data"]["status"] == "completed"

    # Download HTML evaluation report
    dl_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/evaluation-report",
        headers=headers,
    )
    assert dl_res.status_code == 200
    assert "AutoDS — Model Evaluation Report" in dl_res.text

    # Test Celery task
    c_res = evaluate_model_task(dataset_id)
    assert c_res["status"] == "completed"
