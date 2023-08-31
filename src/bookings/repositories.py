from dataclasses import dataclass

from src.base.repositories import BaseRepository
from src.bookings.models import Booking


@dataclass
class BookingRepository(BaseRepository[Booking]):

    async def add_booking(self, booking: Booking) -> Booking:
        return await self.create(booking)
