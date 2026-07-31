import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_analysis_service import AIAnalysisService
from app.services.profiling_service import ProfilingService


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "AI User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "AI Analysis Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_ai_analysis_generation_and_endpoint(async_client: AsyncClient, db_session: AsyncSession) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "ai_test@example.com")

    csv_data = b"customer_id,tenure,monthly_charges,churn\n1,12,65.5,0\n2,2,80.0,1\n3,36,45.0,0\n"
    files = {"file": ("churn.csv", io.BytesIO(csv_data), "text/csv")}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id}, files=files, headers=headers
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Run profiling service first
    profiling_service = ProfilingService(db_session)
    await profiling_service.run_profiling(dataset_id)

    # Run AI Analysis service
    ai_service = AIAnalysisService(db_session)
    analysis = await ai_service.generate_analysis(dataset_id)
    assert analysis.dataset_id == dataset_id
    assert analysis.summary is not None
    assert analysis.recommended_ml_task in ["classification", "regression", "clustering", "none"]

    # Query GET /{dataset_id}/analysis endpoint
    analysis_res = await async_client.get(f"/api/v1/datasets/{dataset_id}/analysis", headers=headers)
    assert analysis_res.status_code == 200
    body = analysis_res.json()
    assert body["success"] is True
    assert "summary" in body["data"]
    assert "quality_assessment" in body["data"]
    assert "insights" in body["data"]


@pytest.mark.asyncio
async def test_ai_analysis_unauthorized_access(async_client: AsyncClient, db_session: AsyncSession) -> None:
    headers_a, project_id_a = await _get_auth_headers_and_project(async_client, "ai_owner_a@example.com")
    headers_b, _ = await _get_auth_headers_and_project(async_client, "ai_owner_b@example.com")

    files = {"file": ("data.csv", io.BytesIO(b"x,y\n1,2\n"), "text/csv")}
    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id_a}, files=files, headers=headers_a
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    profiling_service = ProfilingService(db_session)
    await profiling_service.run_profiling(dataset_id)

    ai_service = AIAnalysisService(db_session)
    await ai_service.generate_analysis(dataset_id)

    # User B attempts to view User A's AI Analysis -> 404
    res_b = await async_client.get(f"/api/v1/datasets/{dataset_id}/analysis", headers=headers_b)
    assert res_b.status_code == 404
