import io
import os
import numpy as np
import pandas as pd
import pytest
from httpx import AsyncClient
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.predictor import predict_with_model
from app.services.automl_service import AutoMLService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.preprocessing_service import PreprocessingService
from app.services.profiling_service import ProfilingService
from app.worker.tasks import predict_batch_task


def test_core_predictor_inference() -> None:
    X_train = pd.DataFrame({"f1": np.random.randn(50), "f2": np.random.randn(50)})
    y_train = pd.Series(np.random.choice([0, 1], size=50))

    clf = RandomForestClassifier(n_estimators=5, random_state=42)
    clf.fit(X_train, y_train)

    test_input = pd.DataFrame({"f1": [0.5], "f2": [-0.2]})
    preds, probas = predict_with_model(clf, test_input)

    assert len(preds) == 1
    assert preds[0] in [0, 1]
    assert probas is not None and len(probas) == 1


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str, str]:
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Predict User", "email": email, "password": "Password123!"},
    )
    user_id = reg_res.json()["data"]["id"]

    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Prediction Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id, user_id


@pytest.mark.asyncio
async def test_prediction_service_and_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id, user_id = await _get_auth_headers_and_project(async_client, "pred_test@example.com")

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
    files = {"file": ("pred_ds.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
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

    # 1. Single Prediction Endpoint
    single_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/predict",
        json={"inputs": {"f1": 2.5, "f2": 3.5}},
        headers=headers,
    )
    assert single_res.status_code == 200
    s_data = single_res.json()["data"]
    assert s_data["prediction_type"] == "single"

    # 2. Batch Prediction Endpoint (JSON)
    batch_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/predict-batch",
        json={"samples": [{"f1": 2.5, "f2": 3.5}, {"f1": 6.5, "f2": 7.5}]},
        headers=headers,
    )
    assert batch_res.status_code == 200
    b_data = batch_res.json()["data"]
    assert b_data["prediction_type"] == "batch"
    prediction_id = b_data["id"]

    # 3. CSV Batch Prediction Endpoint
    test_csv = "f1,f2\n2.5,3.5\n6.5,7.5\n"
    csv_files = {"file": ("batch_input.csv", io.BytesIO(test_csv.encode("utf-8")), "text/csv")}
    csv_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/predict-csv",
        files=csv_files,
        headers=headers,
    )
    assert csv_res.status_code == 200
    assert csv_res.json()["data"]["prediction_type"] == "batch"

    # 4. Download Batch Prediction Results
    dl_res = await async_client.get(
        f"/api/v1/predictions/{prediction_id}/download",
        headers=headers,
    )
    assert dl_res.status_code == 200
    assert "prediction" in dl_res.text

    # 5. Get Prediction History
    hist_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/predictions",
        headers=headers,
    )
    assert hist_res.status_code == 200
    assert len(hist_res.json()["data"]) >= 3

    # 6. Celery Task
    c_res = predict_batch_task(dataset_id, user_id, [{"f1": 1.0, "f2": 2.0}])
    assert c_res["status"] == "completed"
