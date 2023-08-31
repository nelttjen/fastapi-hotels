from dataclasses import dataclass

from src.bookings.models import Booking
from src.bookings.repositories import BookingRepository
from src.base.repositories import Transaction


@dataclass
class BookingService:
    repository: BookingRepository
    transaction: Transaction

    async def add_booking(self, booking: Booking) -> Booking:
        async with self.transaction:
            result = await self.repository.add_booking(booking)
        return result
