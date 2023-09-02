from typing import Optional, Type

from sqlalchemy import select

from src.base.repositories import BaseRepository
from src.base.exceptions import HTTP_EXC, NotFound

from src.hotels.models import Hotel, Room


class HotelRepository(BaseRepository[Hotel | Room]):
    
    async def _get_room_or_exception(
            self, room_id: int, exception: Type[HTTP_EXC], detail: Optional[str] = None
    ) -> Room:
        stmt = select(Room).where(Room.id == room_id)
        result = await self.session.scalar(stmt)
        
        if not result:
            if detail:
                exception = exception(detail=detail)
            raise exception
        
        return result
    
    async def get_room_or_404(self, room_id: int) -> Room:
        return await self._get_room_or_exception(room_id, NotFound, 'Room with this id not found')