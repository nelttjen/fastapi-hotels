import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Literal

from sqlalchemy import MetaData
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker

from src.config import app_settings, db_settings

DEFAULT_ISOLATION_LEVEL: Literal['READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE'] = 'READ COMMITTED'

engine = create_async_engine(
    db_settings.DATABASE_URL,
    isolation_level=DEFAULT_ISOLATION_LEVEL,
)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # noqa
debugger = logging.getLogger('debugger')

metadata = MetaData()
DatabaseModel: DeclarativeMeta = declarative_base(metadata=metadata)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@asynccontextmanager
async def context_db_session() -> AsyncSession:
    session: AsyncSession = async_session_maker()
    yield session
    await session.close()


@listens_for(engine.sync_engine, 'before_cursor_execute', named=True)
def log_query(
        conn, cursor, statement, parameters, context, executemany,
):
    if app_settings.ENABLE_QUERY_DEBUGGING:
        debugger.debug(f'Executing query:\n{statement} with parameters: {parameters}')
