import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_structure(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/health")
    assert response.status_code in [200, 530]
    payload = response.json()
    assert "success" in payload
    assert "status" in payload
    assert "services" in payload
    assert "database" in payload["services"]
    assert "redis" in payload["services"]
