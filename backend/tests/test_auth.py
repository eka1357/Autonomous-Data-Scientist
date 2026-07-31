import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient) -> None:
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "SecurePassword123!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert "user_id" in body["data"]
    assert body["data"]["message"] == "Account created successfully"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(async_client: AsyncClient) -> None:
    payload = {
        "name": "John Doe",
        "email": "duplicate@example.com",
        "password": "SecurePassword123!",
    }
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    body = res2.json()
    assert body["success"] is False
    assert body["error"]["code"] == "USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient) -> None:
    register_payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "Password123!",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "alice@example.com",
        "password": "Password123!",
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


@pytest.mark.asyncio
async def test_login_invalid_password(async_client: AsyncClient) -> None:
    register_payload = {
        "name": "Bob Vance",
        "email": "bob@example.com",
        "password": "Password123!",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "bob@example.com",
        "password": "WrongPassword!",
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_get_me_success(async_client: AsyncClient) -> None:
    register_payload = {
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "password": "Password123!",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "charlie@example.com", "password": "Password123!"},
    )
    access_token = login_res.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    body = me_res.json()
    assert body["success"] is True
    assert body["data"]["email"] == "charlie@example.com"
    assert body["data"]["name"] == "Charlie Brown"


@pytest.mark.asyncio
async def test_get_me_unauthorized(async_client: AsyncClient) -> None:
    me_res = await async_client.get("/api/v1/auth/me")
    assert me_res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_refresh_token_success(async_client: AsyncClient) -> None:
    register_payload = {
        "name": "Dave Miller",
        "email": "dave@example.com",
        "password": "Password123!",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "dave@example.com", "password": "Password123!"},
    )
    refresh_token = login_res.json()["data"]["refresh_token"]

    refresh_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    body = refresh_res.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


@pytest.mark.asyncio
async def test_logout_success(async_client: AsyncClient) -> None:
    register_payload = {
        "name": "Eve Adams",
        "email": "eve@example.com",
        "password": "Password123!",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "eve@example.com", "password": "Password123!"},
    )
    access_token = login_res.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_res = await async_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    body = logout_res.json()
    assert body["success"] is True
    assert body["data"]["message"] == "Logged out successfully"
