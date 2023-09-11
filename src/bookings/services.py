from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional

from src.base.exceptions import Forbidden
from src.base.repositories import Transaction
from src.bookings.models import Booking
from src.bookings.repositories import BookingRepository
from src.bookings.schemas import BookingCreateData
from src.hotels.services import HotelService
from src.users.models import User


@dataclass
class BookingService:
    hotels_service: HotelService
    repository: BookingRepository
    transaction: Transaction

    async def add_booking(
            self, user: User, booking_data: BookingCreateData,
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

    async def get_my_bookings(
            self, user_id: int, booking_id: Optional[int] = None,
    ) -> Sequence[Booking] | Booking:
        return await self.repository.get_my_bookings(user_id, booking_id)

    async def delete_booking(
            self, user_id: int, booking_id: int,
    ) -> None:
        async with self.transaction:
            booking = await self.repository.get_booking_or_404(booking_id)
            if booking.user_id != user_id:
                raise Forbidden('You are not allowed to delete this booking')
            await self.repository.delete(booking)
