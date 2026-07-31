import pytest
from httpx import AsyncClient


async def _get_auth_headers(async_client: AsyncClient, email: str = "project_user@example.com") -> dict[str, str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Project User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_list_projects(async_client: AsyncClient) -> None:
    headers = await _get_auth_headers(async_client, "user1@example.com")

    # Create project
    create_payload = {
        "name": "E-Commerce Churn Workspace",
        "description": "Customer churn analysis dataset workspace",
    }
    create_res = await async_client.post("/api/v1/projects", json=create_payload, headers=headers)
    assert create_res.status_code == 201
    project_data = create_res.json()["data"]
    assert project_data["name"] == "E-Commerce Churn Workspace"
    assert "id" in project_data

    # List projects
    list_res = await async_client.get("/api/v1/projects", headers=headers)
    assert list_res.status_code == 200
    projects_list = list_res.json()["data"]
    assert len(projects_list) == 1
    assert projects_list[0]["id"] == project_data["id"]


@pytest.mark.asyncio
async def test_get_and_update_project(async_client: AsyncClient) -> None:
    headers = await _get_auth_headers(async_client, "user2@example.com")

    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Initial Name", "description": "Initial Desc"},
        headers=headers,
    )
    project_id = create_res.json()["data"]["id"]

    # Get project
    get_res = await async_client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["name"] == "Initial Name"

    # Update project
    update_res = await async_client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Name", "description": "Updated Desc"},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_project(async_client: AsyncClient) -> None:
    headers = await _get_auth_headers(async_client, "user3@example.com")

    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Delete Me", "description": "To be deleted"},
        headers=headers,
    )
    project_id = create_res.json()["data"]["id"]

    delete_res = await async_client.delete(f"/api/v1/projects/{project_id}", headers=headers)
    assert delete_res.status_code == 200

    # Verify 404 on get
    get_res = await async_client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_project_idor_protection(async_client: AsyncClient) -> None:
    headers_user_a = await _get_auth_headers(async_client, "usera@example.com")
    headers_user_b = await _get_auth_headers(async_client, "userb@example.com")

    # User A creates project
    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "User A Private Project"},
        headers=headers_user_a,
    )
    project_id = create_res.json()["data"]["id"]

    # User B attempts to view User A's project -> 404
    get_res = await async_client.get(f"/api/v1/projects/{project_id}", headers=headers_user_b)
    assert get_res.status_code == 404

    # User B attempts to delete User A's project -> 404
    del_res = await async_client.delete(f"/api/v1/projects/{project_id}", headers=headers_user_b)
    assert del_res.status_code == 404
