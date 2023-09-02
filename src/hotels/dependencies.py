from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.base.repositories import Transaction
from src.hotels.services import HotelService
from src.hotels.repositories import HotelRepository


async def get_hotel_service(
        session: Annotated[AsyncSession, Depends(get_db_session)],
):
    repository = HotelRepository(session=session)
    transaction = Transaction(session=session)
    return HotelService(repository=repository, transaction=transaction)
