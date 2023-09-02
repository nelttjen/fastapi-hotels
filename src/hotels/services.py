from dataclasses import dataclass

from src.base.repositories import Transaction
from src.hotels.repositories import HotelRepository
from src.hotels.models import Room


@dataclass
class HotelService:
    repository: HotelRepository
    transaction: Transaction
    
    async def get_room_by_id(self, room_id: int) -> Room:
        return await self.repository.get_room_or_404(room_id)
    