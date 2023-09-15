import datetime

from sqlalchemy import Computed, Date, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DatabaseModel
from src.hotels.models import Room
from src.users.models import User


class Booking(AsyncAttrs, DatabaseModel):
    __tablename__ = 'booking'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, index=True, autoincrement=True,
    )
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('room.id'), nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id'), nullable=False,
    )
    date_from: Mapped[datetime.date] = mapped_column(
        Date, nullable=False,
    )
    date_to: Mapped[datetime.date] = mapped_column(
        Date, nullable=False,
    )
    price: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )
    total_cost: Mapped[int] = mapped_column(
        Integer, Computed('(date_to - date_from) * price'),
    )
    total_days: Mapped[int] = mapped_column(
        Integer, Computed('date_to - date_from'),
    )

    room: Room = relationship(
        'Room', lazy='joined',
    )
    user: User = relationship(
        'User', lazy='joined', back_populates='bookings',
    )
