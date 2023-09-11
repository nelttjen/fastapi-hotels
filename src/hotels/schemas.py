import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.base.exceptions import BadRequest
from src.base.schemas import BaseORMModel


class DateRangeModel(BaseModel):
    date_from: Optional[datetime.date] = Field(default=None)
    date_to: Optional[datetime.date] = Field(default=None)

    def validate_date_to(self):
        """due to empty values from fastapi."""
        if self.date_to <= self.date_from:
            raise BadRequest('Date to must be later than date from')


class HotelBase(BaseORMModel):
    id: int  # noqa
    name: str
    location: str
    image_id: int
    services: List[str]


class HotelInfo(HotelBase):
    rooms_count: int


class HotelWithRoomsLeft(HotelInfo):
    rooms_left: int


class HotelRoomInfo(BaseORMModel):
    id: int  # noqa
    hotel_id: int
    name: str
    description: str
    services: List[str]
    price: int
    image_id: int


class HotelRoomDetailedInfo(HotelRoomInfo):
    quantity: int
    total_cost: int
    rooms_left: int


class HotelRoomInfoWithHotel(HotelRoomInfo):
    hotel: HotelBase
