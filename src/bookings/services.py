from dataclasses import dataclass

from src.bookings.models import Booking
from src.bookings.repositories import BookingRepository
from src.base.repositories import Transaction
from src.bookings.schemas import BookingCreateData
from src.users.models import User
from src.hotels.services import HotelService


@dataclass
class BookingService:
    hotels_service: HotelService
    repository: BookingRepository
    transaction: Transaction

    async def add_booking(
            self, user: User, booking_data: BookingCreateData
    ) -> Booking:
        room_id = booking_data.room_id
        async with self.transaction:
            room = await self.hotels_service.get_room_by_id(room_id)
            await self.repository.check_room_available(room_id, booking_data.date_from, booking_data.date_to)
            booking = Booking(
                user_id=user.id,
                room_id=room_id,
                date_from=booking_data.date_from,
                date_to=booking_data.date_to,
                price=room.price,
            )
            result = await self.repository.add_booking(booking)
        return result
    