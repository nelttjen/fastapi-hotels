from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.bookings.dependencies import get_booking_service
from src.bookings.schemas import BookingCreateData, BookingDetail
from src.bookings.services import BookingService
from src.cache import KeyBuilderCache
from src.users.models import User

bookings_router = APIRouter(
    prefix='/bookings',
    tags=['Bookings'],
)


@bookings_router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
        booking_data: BookingCreateData,
        user: Annotated[User, Depends(get_current_user)],
        booking_service: Annotated[BookingService, Depends(get_booking_service)],
):
    booking_data.validate_date_to()

    await KeyBuilderCache.clear_cache_for_func('get_room_info')
    await KeyBuilderCache.clear_cache_for_func('get_rooms_for_hotel')
    await KeyBuilderCache.clear_cache_for_func('get_hotel_info')

    return await booking_service.add_booking(user, booking_data)


@bookings_router.get(
    '/my',
    status_code=status.HTTP_200_OK,
    response_model=List[BookingDetail],
)
async def get_my_bookings(
        user: Annotated[User, Depends(get_current_user)],
        booking_service: Annotated[BookingService, Depends(get_booking_service)],
):
    return await booking_service.get_my_bookings(user.id)


@bookings_router.get(
    '/my/{booking_id}',
    status_code=status.HTTP_200_OK,
    response_model=BookingDetail,
)
async def get_my_booking(
        booking_id: int,
        user: Annotated[User, Depends(get_current_user)],
        booking_service: Annotated[BookingService, Depends(get_booking_service)],
):
    result = await booking_service.get_my_bookings(user.id, booking_id)
    print(result)
    return result


@bookings_router.delete(
    '/my/{booking_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_my_booking(
        booking_id: int,
        user: Annotated[User, Depends(get_current_user)],
        booking_service: Annotated[BookingService, Depends(get_booking_service)],
):
    return await booking_service.delete_booking(user.id, booking_id)
