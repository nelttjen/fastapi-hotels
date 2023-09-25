from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.dependencies import get_user_service
from src.users.models import User
from src.users.services import RegisterService, UserService


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


@pytest.fixture
async def fake_user(session: AsyncSession) -> User:
    user_service = await get_user_service(session)

    user = User(
        username='fake_user',
        email='fake_email@example.org',
        password=await RegisterService.make_password_hash('fake_password'),
        is_staff=False,
        is_active=True,
        is_superuser=False,
    )
    await user_service.repository.create(user, commit=True)
    return user


@pytest.fixture
async def user_service(session) -> UserService:
    return await get_user_service(session)
