import datetime

from pydantic import field_validator

from src.base.schemas import BaseORMModel
from src.base.utils import get_utcnow
from src.hotels.schemas import DateRangeModel, HotelRoomInfoWithHotel


class BookingCreateData(DateRangeModel):
    room_id: int

    @field_validator('date_from')
    def validate_date_from(cls, value):  # noqa
        if value <= get_utcnow().date():
            raise ValueError('Date must be tomorrow or later')
        return value


class BookingDetail(BaseORMModel):
    id: int  # noqa
    room: HotelRoomInfoWithHotel
    date_from: datetime.date
    date_to: datetime.date
    price: int
    total_cost: int
    total_days: int
