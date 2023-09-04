from typing import List

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DatabaseModel


class Hotel(DatabaseModel):
    __tablename__ = 'hotel'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, index=True, autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False,
    )
    location: Mapped[str] = mapped_column(
        String, nullable=False,
    )
    services: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list, server_default='[]',
    )
    rooms_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default='0',
    )
    image_id: Mapped[int] = mapped_column(
        Integer, nullable=True,
    )

    # relationship
    rooms: List['Room'] = relationship(
        'Room', back_populates='hotel', lazy='select',
    )


class Room(AsyncAttrs, DatabaseModel):
    __tablename__ = 'room'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, index=True, autoincrement=True,
    )
    hotel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('hotel.id', ondelete='CASCADE'), nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String,
    )
    price: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )
    services: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list, server_default='[]',
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default='0',
    )
    image_id: Mapped[int] = mapped_column(
        Integer, nullable=True,
    )

    # rel
    hotel: 'Hotel' = relationship(
        'Hotel', back_populates='rooms', lazy='joined',
    )
