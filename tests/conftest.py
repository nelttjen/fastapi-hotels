import os

os.environ['MODE'] = 'TEST'

import asyncio
import functools
from typing import List

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from migrations import __models__  # noqa
from src.auth.services import RegisterService
from src.config import app_settings
from src.database import DatabaseModel, context_db_session, engine
from src.users.dependencies import get_user_service
from src.users.models import User


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
async def session():
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
            password=RegisterService.make_password_hash(f'user_{i + 1}'),
            **param,
        )
        for i, param in enumerate(params)
    ]
    await user_service.repository.bulk_create(users, commit=True)
    return users
