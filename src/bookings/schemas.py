import datetime

from pydantic import BaseModel, field_validator
from src.base.exceptions import BadRequest


class BookingCreateData(BaseModel):
    room_id: int
    date_from: datetime.date
    date_to: datetime.date
    
    @field_validator("date_from")
    def validate_date_from(cls, v):
        if v <= datetime.datetime.utcnow().date():
            raise ValueError('Date must be tomorrow or later')
        return v
    
    def validate_date_to(self):
        """due to emtry values from fastapi"""
        if self.date_to <= self.date_from:
            raise BadRequest('Date to must be later than date from')