import pytest_asyncio

from src.account.schemas import CreateUserSchema
from src.account.services.user import UserService


@pytest_asyncio.fixture(scope='session')
async def get_user_payload():
    test_email = "test@test.com"
    test_first_name = "Test"
    test_last_name = "Testovich"
    return {
        "email": test_email,
        "first_name": test_first_name,
        "last_name": test_last_name
    }

@pytest_asyncio.fixture(scope='session')
async def get_update_payload():
    test_update_first_name = "TestNew"
    test_update_last_name = "TestovichNew"
    return {
        "first_name": test_update_first_name,
        "last_name": test_update_last_name
    }

@pytest_asyncio.fixture
async def create_test_user(async_session,get_user_payload):
    user_service = UserService(async_session)
    user_schema = CreateUserSchema(**get_user_payload)
    return await user_service.create(user_schema=user_schema)