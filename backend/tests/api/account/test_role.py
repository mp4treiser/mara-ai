import pytest


@pytest.mark.asyncio
async def test_healthcheck(async_client):
    response = await async_client.get("/api/v1/account/roles/")
    assert response.status_code == 200