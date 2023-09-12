from os import PathLike
from pathlib import Path
from typing import List

from sqlalchemy import JSON, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import IMAGES_URL
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

    @property
    def images(self) -> dict[str, PathLike[Path]]:
        filename = f'{self.image_id}.webp'
        return {
            'original': IMAGES_URL / filename,
            '1920x1080': IMAGES_URL / 'resized/1920_1080' / ('resized_1920_1080' + filename),
            '1024x562': IMAGES_URL / 'resized/1024_562' / ('resized_1024_562' + filename),
            '200x100': IMAGES_URL / 'resized/200_100' / ('resized_200_100' + filename),
        }


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

    @property
    def images(self) -> dict[str, PathLike[Path]]:
        filename = f'{self.image_id}.webp'
        return {
            'original': IMAGES_URL / filename,
            '1920x1080': IMAGES_URL / 'resized/1920_1080' / ('resized_1920_1080' + filename),
            '1024x562': IMAGES_URL / 'resized/1024_562' / ('resized_1024_562' + filename),
            '200x100': IMAGES_URL / 'resized/200_100' / ('resized_200_100' + filename),
        }


class FavouriteHotel(DatabaseModel):
    __tablename__ = 'favourite_hotel'
    __table_args__ = (
        UniqueConstraint('user_id', 'hotel_id', name='unique_user_hotel_fav_constraint'),
    )

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, index=True, autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False,
    )
    hotel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('hotel.id', ondelete='CASCADE'), nullable=False,
    )
