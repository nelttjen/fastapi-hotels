import pytest

from src.auth.dependencies import get_auth_service
from src.auth.services import AuthService
from src.users.services import UserService


@pytest.fixture
async def auth_service(user_service: UserService) -> AuthService:
    return await get_auth_service(user_service)
