import logging
import datetime
from typing import List, Optional, Type

from sqlalchemy import and_, func, or_, select

from src.database import engine
from src.base.repositories import BaseRepository
from src.base.exceptions import HTTP_EXC, NotFound
from src.bookings.repositories import BookingRepository
from src.hotels.models import Hotel, Room
from src.bookings.models import Booking

debugger = logging.getLogger('debugger')


class HotelRepository(BaseRepository[Hotel | Room]):

    async def _get_room_or_exception(
            self, room_id: int, exception: Type[HTTP_EXC], detail: Optional[str] = None,
    ) -> Room:
        stmt = select(Room).where(Room.id == room_id)
        result = await self.session.scalar(stmt)

        if not result:
            if detail:
                exception = exception(detail=detail)
            raise exception

        return result

    async def _get_hotel_or_exception(
            self, hotel_id: int, exception: Type[HTTP_EXC], detail: Optional[str] = None,
    ) -> Hotel:
        stmt = select(Hotel).where(Hotel.id == hotel_id)
        result = await self.session.scalar(stmt)

        if not result:
            if detail:
                exception = exception(detail=detail)
            raise exception

        return result

    async def get_hotel_or_404(self, hotel_id: int) -> Hotel:
        return await self._get_hotel_or_exception(hotel_id, NotFound, 'Hotel with this id not found')

    async def get_room_or_404(self, room_id: int) -> Room:
        return await self._get_room_or_exception(room_id, NotFound, 'Room with this id not found')

    async def search_hotels(
            self, name: str, date_from: datetime.date, date_to: datetime.date,
    ):
        """"""
        """
        with const(curr_date) as (
            values (date('2023-09-04'))
        ), booked_rooms_by_hotels as (
            select count(b.id) as rooms_booked, h.id as hotel_id from booking b
            join const on true
            left join room r on r.id = b.room_id
            inner join hotel h on h.id = r.hotel_id and (h.name ilike '%алтай%' or h.location ilike '%алтай%')
            WHERE b.date_from <= const.curr_date AND b.date_to >= const.curr_date OR
                  b.date_from > const.curr_date AND b.date_to < const.curr_date OR
                  b.date_from <= const.curr_date AND b.date_to >= const.curr_date AND b.date_to < const.curr_date OR
                  b.date_from > const.curr_date AND b.date_from <= const.curr_date AND b.date_to >= const.curr_date
            group by r.hotel_id, h.id
        ), rooms_by_hotels as (
            select h.id as hotel_id, sum(room.quantity) as rooms_count from room
            left join hotel h on h.id = room.hotel_id
            where h.name ilike '%алтай%' or h.location ilike '%алтай%'
            group by room.hotel_id, h.id
        )
        select h.id, h.name, h.image_id, (rbh.rooms_count - br.rooms_booked) as rooms_left from hotel h
        join booked_rooms_by_hotels br on br.hotel_id = h.id
        join rooms_by_hotels rbh on rbh.hotel_id = h.id
        where h.name ilike '%алтай%' or h.location ilike '%алтай%' and rbh.rooms_count > br.rooms_booked;
        """
        booked_by_hotels = await self.get_booked_by_hotels(date_from=date_from, date_to=date_to, name=name)

        rooms_by_hotels = await self.get_rooms_by_hotels(name=name)

        hotels = select(
            Hotel.id,
            Hotel.name,
            Hotel.image_id,
            Hotel.services,
            (rooms_by_hotels.c.rooms_count - func.coalesce(booked_by_hotels.c.rooms_booked, 0)).label('rooms_left'),
            rooms_by_hotels.c.rooms_count.label('rooms_count'),
        ).select_from(Hotel).join(
            booked_by_hotels, booked_by_hotels.c.hotel_id == Hotel.id, isouter=True,
        ).join(
            rooms_by_hotels, rooms_by_hotels.c.hotel_id == Hotel.id,
        ).where(and_(
            or_(Hotel.name.ilike(f'%{name}%'), Hotel.location.ilike(f'%{name}%')),
            rooms_by_hotels.c.rooms_count > func.coalesce(booked_by_hotels.c.rooms_booked, 0),
        ))

        result = await self.session.execute(hotels)
        return result.mappings().all()

    async def get_hotel_info(self, hotel_id: int) -> Hotel:
        stmt = select(Hotel, func.coalesce(func.sum(Room.quantity), 0)).join(
            Room, Room.hotel_id == Hotel.id, isouter=True,
        ).where(Hotel.id == hotel_id)
        return await self.session.scalar(stmt)

    async def get_hotel_rooms_available(
            self, hotel_id: int, date_from: datetime.date, date_to: datetime.date,
    ):
        clauses = await BookingRepository.get_booked_rooms_clauses(date_from, date_to)
        booked_rooms = select(
            Room.id.label('room_id'),
            func.coalesce(func.count(Booking.id), 0).label('rooms_booked'),
        ).select_from(Room).join(
            Booking, Booking.room_id == Room.id, isouter=True,
        ).where(and_(Room.hotel_id == hotel_id, or_(*clauses))).group_by(Room.id).cte('booked_rooms')

        rooms = select(
            Room.__table__.columns,  # noqa
            (Room.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)).label('rooms_left'),
            (Room.price * (date_to - date_from).days).label('total_cost'),
        ).select_from(Room).join(
            booked_rooms, booked_rooms.c.room_id == Room.id, isouter=True,
        ).where(Room.hotel_id == hotel_id)

        result = await self.session.execute(rooms)

        return result.mappings().all()

    @staticmethod
    async def get_hotel_join(name: Optional[str] = None, hotel_ids: Optional[List[int]] = None,):
        if not name and not hotel_ids:
            raise RuntimeError('name or hotel_id required for get_rooms_by_hotels')
        hotel_join_clause = None

        if name is not None:
            hotel_join_clause = and_(Hotel.id == Room.hotel_id, or_(
                Hotel.name.ilike(f'%{name}%'), Hotel.location.ilike(f'%{name}%'),
            ))
        if hotel_ids is not None:
            hotel_join_clause = Hotel.id.in_(hotel_ids)
        return hotel_join_clause

    @classmethod
    async def get_rooms_by_hotels(
            cls, name: Optional[str] = None, hotel_ids: Optional[List[int]] = None,
    ):
        hotel_join_clause = await cls.get_hotel_join(name=name, hotel_ids=hotel_ids)

        return select(
            Hotel.id.label('hotel_id'),
            func.sum(Room.quantity).label('rooms_count'),
        ).select_from(Room).join(
            Hotel, hotel_join_clause,
        ).group_by(Hotel.id).cte('rooms_by_hotels')

    @classmethod
    async def get_booked_by_hotels(
            cls, date_from: datetime.date, date_to: datetime.date,
            name: Optional[str] = None, hotel_ids: Optional[List[int]] = None,
    ):
        hotel_join_clause = await cls.get_hotel_join(name=name, hotel_ids=hotel_ids)

        clauses = await BookingRepository.get_booked_rooms_clauses(date_from, date_to)

        return select(
            func.count(Booking.id).label('rooms_booked'),
            Hotel.id.label('hotel_id'),
        ).select_from(Booking).join(
            Room, Room.id == Booking.room_id, isouter=True,
        ).join(
            Hotel, hotel_join_clause,
        ).where(or_(*clauses)).group_by(Hotel.id).cte('booked_by_hotels')