import pytest
from httpx import AsyncClient
from src.app import app as fastapi_app
from src.auth.jwt import create_access_token
from src.users.models import User


@pytest.fixture(scope='function')
async def ac() -> AsyncClient:
    async with AsyncClient(app=fastapi_app, base_url='http://test') as client:
        yield client


@pytest.fixture(scope='function')
async def auth_ac(superuser: User) -> AsyncClient:
    token = create_access_token(superuser)
    async with AsyncClient(
        app=fastapi_app,
        base_url='http://test',
        headers={
            'Authorization': f'Bearer {token}',
        },
    ) as client:
        yield client
