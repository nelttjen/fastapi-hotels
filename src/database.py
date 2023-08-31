import logging
from typing import AsyncGenerator

from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeMeta
from sqlalchemy import MetaData

from src.config import db_settings, config


engine = create_async_engine(db_settings.DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # noqa
debugger = logging.getLogger('debugger')

metadata = MetaData()
DatabaseModel: DeclarativeMeta = declarative_base(metadata=metadata)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@listens_for(engine.sync_engine, 'before_cursor_execute', named=True)
def log_query(
        conn, cursor, statement, parameters, context, executemany,
):
    if config('ENABLE_QUERY_DEBUGGING', False):
        debugger.debug(f'Executing query:\n{statement} with parameters: {parameters}')
