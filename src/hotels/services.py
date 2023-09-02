import datetime
from dataclasses import dataclass

from src.base.exceptions import NotFound
from src.base.repositories import Transaction
from src.hotels.repositories import HotelRepository
from src.hotels.models import Room, Hotel


@dataclass
class HotelService:
    repository: HotelRepository
    transaction: Transaction

    async def get_room_by_id(self, room_id: int) -> Room:
        return await self.repository.get_room_or_404(room_id)

    async def get_hotels_by_name(
            self, name: str, date_from: datetime.date, date_to: datetime.date,
    ) -> list[Hotel]:
        name = name.strip().lower()
        return await self.repository.search_hotels(name, date_from, date_to)

    async def get_hotel_info(self, hotel_id: int) -> Hotel:
        result = await self.repository.get_hotel_info(hotel_id)
        if not Hotel:
            raise NotFound('Hotel with this id does not exist')
        return result

    async def get_hotel_rooms(
            self, hotel_id: int, date_from: datetime.date, date_to: datetime.date,
    ):
        return await self.repository.get_hotel_rooms_available(hotel_id, date_from, date_to)
