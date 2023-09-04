from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.repositories import Transaction
from src.database import get_db_session
from src.users.repositories import UserRepository
from src.users.services import UserService


async def get_user_service(
        session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    repository = UserRepository(session=session)
    transaction = Transaction(session=session)
    return UserService(repository=repository, transaction=transaction)
