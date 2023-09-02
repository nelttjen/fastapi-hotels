import datetime

from fastapi import APIRouter, Depends
from typing import Annotated

from starlette import status

from src.auth.dependencies import get_current_user
from src.bookings.services import BookingService
from src.bookings.dependencies import get_booking_service
from src.bookings.models import Booking
from src.bookings.schemas import BookingCreateData
from src.users.models import User

bookings_router = APIRouter(
    prefix='/bookings',
    tags=['Bookings'],
)


@bookings_router.post(
    '/create/',
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_data: BookingCreateData,
    user: Annotated[User, Depends(get_current_user)],
    booking_service: Annotated[BookingService, Depends(get_booking_service)],
):
    booking_data.validate_date_to()
    return await booking_service.add_booking(user, booking_data)
