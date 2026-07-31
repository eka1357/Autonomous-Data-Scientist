import io
import pytest
from httpx import AsyncClient


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Dataset User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Upload Target Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_upload_csv_dataset_success(async_client: AsyncClient) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "ds_user1@example.com")

    csv_content = b"id,age,income,churn\n1,25,50000,0\n2,30,60000,1\n"
    files = {"file": ("test_churn.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"project_id": project_id}

    response = await async_client.post("/api/v1/datasets/upload", data=data, files=files, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["filename"] == "test_churn.csv"
    assert "dataset_id" in body["data"]

    dataset_id = body["data"]["dataset_id"]

    # Verify get details
    get_res = await async_client.get(f"/api/v1/datasets/{dataset_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["filename"] == "test_churn.csv"


@pytest.mark.asyncio
async def test_upload_invalid_extension(async_client: AsyncClient) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "ds_user2@example.com")

    files = {"file": ("unsupported_script.py", io.BytesIO(b"print('hello')"), "text/plain")}
    data = {"project_id": project_id}

    response = await async_client.post("/api/v1/datasets/upload", data=data, files=files, headers=headers)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"


@pytest.mark.asyncio
async def test_upload_empty_file(async_client: AsyncClient) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "ds_user3@example.com")

    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    data = {"project_id": project_id}

    response = await async_client.post("/api/v1/datasets/upload", data=data, files=files, headers=headers)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_FILE"


@pytest.mark.asyncio
async def test_delete_dataset(async_client: AsyncClient) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "ds_user4@example.com")

    csv_content = b"col1,col2\nval1,val2\n"
    files = {"file": ("data_to_delete.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"project_id": project_id}

    upload_res = await async_client.post("/api/v1/datasets/upload", data=data, files=files, headers=headers)
    dataset_id = upload_res.json()["data"]["dataset_id"]

    delete_res = await async_client.delete(f"/api/v1/datasets/{dataset_id}", headers=headers)
    assert delete_res.status_code == 200

    # Verify 404
    get_res = await async_client.get(f"/api/v1/datasets/{dataset_id}", headers=headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_dataset_idor_protection(async_client: AsyncClient) -> None:
    headers_a, project_id_a = await _get_auth_headers_and_project(async_client, "owner_a@example.com")
    headers_b, _ = await _get_auth_headers_and_project(async_client, "owner_b@example.com")

    # Owner A uploads dataset
    files = {"file": ("secret_data.csv", io.BytesIO(b"a,b\n1,2\n"), "text/csv")}
    upload_res = await async_client.post(
        "/api/v1/datasets/upload", data={"project_id": project_id_a}, files=files, headers=headers_a
    )
    dataset_id = upload_res.json()["data"]["dataset_id"]

    # Owner B attempts to view -> 404
    get_res = await async_client.get(f"/api/v1/datasets/{dataset_id}", headers=headers_b)
    assert get_res.status_code == 404

    # Owner B attempts to delete -> 404
    del_res = await async_client.delete(f"/api/v1/datasets/{dataset_id}", headers=headers_b)
    assert del_res.status_code == 404
