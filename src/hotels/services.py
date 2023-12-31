import datetime
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import RowMapping

from src.base.exceptions import NotFound
from src.base.repositories import Transaction
from src.hotels.models import Hotel, Room
from src.hotels.repositories import HotelRepository


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

    async def get_hotel_info(self, hotel_id: int) -> RowMapping:
        result = await self.repository.get_hotel_info(hotel_id)
        if not Hotel:
            raise NotFound('Hotel with this id does not exist')
        return result

    async def get_hotel_rooms(
            self, hotel_id: int, date_from: datetime.date, date_to: datetime.date, room_id: Optional[int] = None,
    ) -> Sequence[RowMapping]:
        return await self.repository.get_hotel_rooms_info(hotel_id, date_from, date_to, room_id=room_id)

    async def get_my_favourite_hotels(self, user_id: int) -> Sequence[RowMapping]:
        return await self.repository.get_my_favourite_hotels(user_id)

    async def add_favourite_hotel(self, user_id: int, hotel_id: int) -> bool:
        return await self.repository.add_favourite_hotel(user_id, hotel_id)

    async def remove_favourite_hotel(self, user_id: int, hotel_id) -> None:
        await self.repository.remove_favourite_hotel(user_id, hotel_id)
