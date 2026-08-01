import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_endpoint(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/health/liveness")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_endpoint(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/health/readiness")
    # Will be 200 if Postgres/Redis mock or running, or 503 if services offline
    assert res.status_code in [200, 503]
    data = res.json()
    assert "services" in data


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(async_client: AsyncClient) -> None:
    res = await async_client.get("/metrics")
    assert res.status_code == 200
    assert "http_requests_total" in res.text or "http_request_duration_seconds" in res.text
