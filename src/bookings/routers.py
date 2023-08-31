import datetime

from fastapi import APIRouter, Depends
from typing import Annotated

from src.bookings.services import BookingService
from src.bookings.dependencies import get_booking_service
from src.bookings.models import Booking

bookings_router = APIRouter(
    prefix='/bookings',
    tags=['Bookings'],
)


@bookings_router.get('')
async def get_all_bookings(
        service: Annotated[BookingService, Depends(get_booking_service)],
):
    return


@bookings_router.get('/{booking_id}')
async def get_booking_info(booking_id: int):
    return
