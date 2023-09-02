from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.bookings.repositories import BookingRepository
from src.base.repositories import Transaction
from src.bookings.services import BookingService
from src.hotels.repositories import HotelRepository
from src.hotels.services import HotelService


async def get_booking_service(
        session: AsyncSession = Depends(get_db_session),
) -> BookingService:
    repository = BookingRepository(session=session)
    transaction = Transaction(session=session)
    
    hotel_repository = HotelRepository(session=session)
    hotel_service = HotelService(repository=hotel_repository, transaction=transaction)
    
    return BookingService(repository=repository, transaction=transaction, hotels_service=hotel_service)
