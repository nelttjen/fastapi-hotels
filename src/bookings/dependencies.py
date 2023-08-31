from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.bookings.repositories import BookingRepository
from src.base.repositories import Transaction
from src.bookings.services import BookingService


async def get_booking_service(
        session: AsyncSession = Depends(get_db_session),
) -> BookingService:
    repository = BookingRepository(session=session)
    transaction = Transaction(session=session)
    return BookingService(repository=repository, transaction=transaction)
