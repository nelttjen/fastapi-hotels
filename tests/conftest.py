import logging
import os

from pymongo import MongoClient
from pymongo.database import Database

os.environ['MODE'] = 'TEST'

import asyncio
import functools
from typing import List, Optional

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from migrations import __models__  # noqa
from src.app import app as fastapi_app
from src.auth.dependencies import get_auth_service
from src.auth.jwt import create_access_token
from src.auth.services import AuthService, RegisterService
from src.auth.models import EmailCodeSent, VerificationCode
from src.config import app_settings, mongo_settings
from src.database import DatabaseModel, context_db_session, engine
from src.users.dependencies import get_user_service
from src.users.models import User
from src.users.services import UserService


debugger = logging.getLogger('debugger')


async def perform_clean_db(db_session: Optional[AsyncSession] = None, mongo_session: Optional[Database] = None):
    if db_session is not None:
        await db_session.execute(delete(User))
        await db_session.commit()

    if mongo_session is not None:
        code_collection = mongo_session.get_collection(EmailCodeSent.Meta.__collection__)
        verification_collection = mongo_session.get_collection(VerificationCode.Meta.__collection__)
        code_collection.delete_many({})
        verification_collection.delete_many({})


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert app_settings.MODE == 'TEST'
    os.environ['SINGLE_CLEAN'] = '0'

    async with engine.begin() as conn:
        await conn.run_sync(DatabaseModel.metadata.drop_all)
        await conn.run_sync(DatabaseModel.metadata.create_all)


@pytest.fixture(scope='function', autouse=True)
async def cleanup_database(session: AsyncSession, mongo_session: Database, request):
    assert app_settings.MODE == 'TEST'

    function_name = list(request.keywords)[0].split('[')[0]

    if 'disable_clean' in request.keywords:
        if not int(os.environ.get('SINGLE_CLEAN', '1')) or function_name != os.environ.get('LAST_FUNCTION'):
            await perform_clean_db(db_session=session, mongo_session=mongo_session)
            os.environ['SINGLE_CLEAN'] = '1'
        os.environ['LAST_FUNCTION'] = function_name
        return

    os.environ['SINGLE_CLEAN'] = '0'

    await perform_clean_db(db_session=session, mongo_session=mongo_session)


@pytest.fixture(scope='function')
async def session() -> AsyncSession:
    async with context_db_session() as conn:
        yield conn


@pytest.fixture(scope='function')
async def mongo_session():
    client = MongoClient(**mongo_settings.MONGODB_AUTHPARAMS)
    db = client.get_database(mongo_settings.MONGODB_DB)
    yield db
    client.close()


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

from tests.fixtures.users       import *    # noqa
from tests.fixtures.auth        import *    # noqa
from tests.fixtures.client      import *    # noqa
