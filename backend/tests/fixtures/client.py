import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from tests.constants import BASE_TEST_URL

@pytest_asyncio.fixture(scope='session')
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=BASE_TEST_URL
    ) as client:
        yield client