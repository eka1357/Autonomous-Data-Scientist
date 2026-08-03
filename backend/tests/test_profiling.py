import io
import tempfile
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.profiler import profile_csv_file
from app.services.profiling_service import ProfilingService


def test_profile_csv_file_computation() -> None:
    csv_content = (
        "name,age,salary\n"
        "Alice,25,50000\n"
        "Bob,,60000\n"
        "Charlie,35,70000\n"
        "Alice,25,50000\n"  # Duplicate row
    )

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False, encoding="utf-8") as tmp:
        tmp.write(csv_content)
        tmp.flush()
        tmp_path = tmp.name

    result = profile_csv_file(tmp_path)

    assert result["row_count"] == 4
    assert result["column_count"] == 3
    assert result["column_names"] == ["name", "age", "salary"]
    assert result["missing_values"]["age"] == 1
    assert result["missing_values"]["name"] == 0
    assert result["duplicate_row_count"] == 1

    assert "age" in result["summary_stats"]
    assert "salary" in result["summary_stats"]
    assert result["summary_stats"]["salary"]["min"] == 50000.0
    assert result["summary_stats"]["salary"]["max"] == 70000.0


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Profiler User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Profiling Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_profiling_service_and_endpoint(async_client: AsyncClient, db_session: AsyncSession) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "profiler_test@example.com")

    csv_data = b"item,price,quantity\nApple,1.5,10\nBanana,0.8,20\nApple,1.5,10\n"
    files = {"file": ("items.csv", io.BytesIO(csv_data), "text/csv")}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id}, files=files, headers=headers
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Run profiling service
    profiling_service = ProfilingService(db_session)
    profile = await profiling_service.run_profiling(dataset_id)
    assert profile.dataset_id == dataset_id

    # Query GET /{dataset_id}/profile endpoint
    profile_res = await async_client.get(f"/api/v1/datasets/{dataset_id}/profile", headers=headers)
    assert profile_res.status_code == 200
    body = profile_res.json()
    assert body["success"] is True
    assert body["data"]["duplicate_row_count"] == 1
    assert "price" in body["data"]["summary_stats"]


@pytest.mark.asyncio
async def test_profiling_unauthorized_access(async_client: AsyncClient, db_session: AsyncSession) -> None:
    headers_a, project_id_a = await _get_auth_headers_and_project(async_client, "prof_owner_a@example.com")
    headers_b, _ = await _get_auth_headers_and_project(async_client, "prof_owner_b@example.com")

    files = {"file": ("data.csv", io.BytesIO(b"x,y\n1,2\n"), "text/csv")}
    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id_a}, files=files, headers=headers_a
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    profiling_service = ProfilingService(db_session)
    await profiling_service.run_profiling(dataset_id)

    # Owner B tries to access Owner A's dataset profile -> 404
    res_b = await async_client.get(f"/api/v1/datasets/{dataset_id}/profile", headers=headers_b)
    assert res_b.status_code == 404


def test_concert_tours_numeric_coercion() -> None:
    concert_csv_content = (
        "Artist,Actual gross,Adjusted gross,Tour,Shows\n"
        'Ed Sheeran,"$432,400,000","$481,200,000",Divide Tour,255\n'
        'U2,"$736,421,584","$860,000,000",360 Tour,110\n'
        'Guns N Roses,"$584,200,000","$620,000,000",Not in This Lifetime,158\n'
    )

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False, encoding="utf-8") as tmp:
        tmp.write(concert_csv_content)
        tmp.flush()
        tmp_path = tmp.name

    result = profile_csv_file(tmp_path)

    assert result["data_types"]["Actual gross"] in ("float64", "int64")
    assert result["data_types"]["Adjusted gross"] in ("float64", "int64")
    assert "Actual gross" in result["summary_stats"]
    assert "Adjusted gross" in result["summary_stats"]
    assert result["summary_stats"]["Actual gross"]["max"] == 736421584.0

