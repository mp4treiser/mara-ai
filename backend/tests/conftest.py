import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from tests.fixtures.database import TestDatabase

pytest_plugins = [
    "tests.fixtures.client",
    "tests.fixtures.async_session",
    "tests.fixtures.user"
]


@pytest_asyncio.fixture
async def test_db():
    db = TestDatabase()
    await db.create_database()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def create_tables(test_db):
    await test_db.create_tables()
    yield


@pytest_asyncio.fixture
async def async_session(test_db) -> AsyncSession:
    async with test_db.session_maker() as session:
        yield session  # noqa
        await session.rollback()