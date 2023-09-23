import os

os.environ['MODE'] = 'TEST'

import asyncio
import functools
from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from migrations import __models__  # noqa
from src.app import app as fastapi_app
from src.auth.dependencies import get_auth_service
from src.auth.jwt import create_access_token
from src.auth.services import AuthService, RegisterService
from src.config import app_settings
from src.database import DatabaseModel, context_db_session, engine
from src.users.dependencies import get_user_service
from src.users.models import User
from src.users.services import UserService


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert app_settings.MODE == 'TEST'

    async with engine.begin() as conn:
        await conn.run_sync(DatabaseModel.metadata.drop_all)
        await conn.run_sync(DatabaseModel.metadata.create_all)


@pytest.fixture(scope='function', autouse=True)
async def cleanup_database():
    assert app_settings.MODE == 'TEST'

    async with context_db_session() as conn:
        await conn.execute(delete(User))
        await conn.commit()


@pytest.fixture(scope='function')
async def session() -> AsyncSession:
    async with context_db_session() as conn:
        yield conn


@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


def override_settings(target, attr, value):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            previous_value = getattr(target, attr)
            setattr(target, attr, value)

            result = await func(*args, **kwargs)

            setattr(target, attr, previous_value)

            return result

        return wrapper

    return decorator


@pytest.fixture
async def users(session: AsyncSession) -> List[User]:

    user_service = await get_user_service(session)

    params = [
        {'is_staff': True, 'is_active': True, 'is_superuser': True},
        {'is_staff': True, 'is_active': True, 'is_superuser': False},
        {'is_staff': False, 'is_active': True, 'is_superuser': False},
        {'is_staff': False, 'is_active': False, 'is_superuser': False},
    ]
    users = [
        User(
            username=f'user_{i + 1}',
            email=f'user_{i + 1}@example.com',
            password=await RegisterService.make_password_hash(f'user_{i + 1}'),
            **param,
        )
        for i, param in enumerate(params)
    ]
    await user_service.repository.bulk_create(users, commit=True)
    return users


@pytest.fixture
async def superuser(session: AsyncSession) -> User:
    user_service = await get_user_service(session)

    user = User(
        username='admin',
        email='admin@example.org',
        password=await RegisterService.make_password_hash('admin'),
        is_staff=True,
        is_active=True,
        is_superuser=True,
    )
    await user_service.repository.create(user, commit=True)
    return user


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


@pytest.fixture
async def user_service(session) -> UserService:
    return await get_user_service(session)


@pytest.fixture
async def auth_service(user_service: UserService) -> AuthService:
    return await get_auth_service(user_service)
