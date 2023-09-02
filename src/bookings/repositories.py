import datetime
import logging
from dataclasses import dataclass

from sqlalchemy import select, func, and_, or_

from src.database import engine
from src.base.repositories import BaseRepository
from src.bookings.models import Booking
from src.hotels.models import Room
from src.bookings.exceptions import NoRoomsAvailable


logger = logging.getLogger('all')


@dataclass
class BookingRepository(BaseRepository[Booking]):

    async def add_booking(self, booking: Booking) -> Booking:
        return await self.create(booking)
    
    async def check_room_available(
            self, room_id: int, date_from: datetime.date, date_to: datetime.date
    ) -> None:
        clauses = [
            and_(Booking.date_from <= date_from, Booking.date_to >= date_to),
            and_(Booking.date_from > date_from, Booking.date_to < date_to),
            and_(Booking.date_from <= date_from, Booking.date_to >= date_from, Booking.date_to < date_to),
            and_(Booking.date_from > date_from, Booking.date_from <= date_to, Booking.date_to >= date_to),
        ]
        booked_rooms = select(Booking.room_id).where(
            and_(
                Booking.room_id == room_id,
                or_(*clauses),
            )
        ).cte('booked_rooms')
        
        rooms_left = select(
            (Room.quantity - func.count(booked_rooms.c.room_id)).label('rooms_left')
        ).select_from(Room).join(
            booked_rooms, Room.id == booked_rooms.c.room_id, isouter=True,
        ).where(Room.id == room_id).group_by(Room.quantity, booked_rooms.c.room_id)
        
        logger.debug(rooms_left.compile(engine, compile_kwargs={'literal_binds': True}))
        
        result = await self.session.scalar(rooms_left)
        if result <= 0:
            if result < 0:
                logger.warning(f'Rooms has less than 0 available, {result}')
            raise NoRoomsAvailable
        