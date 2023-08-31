import datetime
from typing import Any

from src.database import DatabaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, JSON, Date, Computed


class Booking(DatabaseModel):
    __tablename__ = 'booking'

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
