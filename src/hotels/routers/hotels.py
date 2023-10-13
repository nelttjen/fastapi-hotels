from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from src.auth.dependencies import get_current_user
from src.base.schemas import DetailModel, SuccessModel
from src.hotels.dependencies import get_hotel_service
from src.hotels.schemas import DateRangeModel, HotelInfo, HotelWithRoomsLeft
from src.hotels.services import HotelService
from src.users.models import User

hotels_router = APIRouter(
    prefix='/hotels',
)


@hotels_router.get(
    '/search/{name}',
    status_code=status.HTTP_200_OK,
    response_model=List[HotelWithRoomsLeft],
)
@cache(expire=60 * 30, namespace='clearable-search_available_hotels')
async def search_available_hotels(
        name: str,
        filters: Annotated[DateRangeModel, Depends()],
        hotel_service: Annotated[HotelService, Depends(get_hotel_service)],
):
    return await hotel_service.get_hotels_by_name(name, filters.date_from, filters.date_to)


@hotels_router.get(
    '/{hotel_id}',
    status_code=status.HTTP_200_OK,
    response_model=HotelInfo,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'model': DetailModel,
            'description': 'Hotel not found',
        },
    },
)
@cache(expire=60 * 30, namespace='clearable-get_hotel_info')
async def get_hotel_info(
        hotel_id: int,
        hotel_service: Annotated[HotelService, Depends(get_hotel_service)],
):
    return await hotel_service.get_hotel_info(hotel_id)


@hotels_router.get(
    '/my/favourites',
    status_code=status.HTTP_200_OK,
    response_model=List[HotelInfo],
)
async def get_favourite_hotels(
        hotel_service: Annotated[HotelService, Depends(get_hotel_service)],
        user: Annotated[User, Depends(get_current_user)],
):
    return await hotel_service.get_my_favourite_hotels(user.id)


@hotels_router.post(
    '/my/favourites/{hotel_id}',
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessModel,
)
async def add_favourite_hotel(
        hotel_id: int,
        hotel_service: Annotated[HotelService, Depends(get_hotel_service)],
        user: Annotated[User, Depends(get_current_user)],
):
    success = await hotel_service.add_favourite_hotel(user.id, hotel_id)
    return SuccessModel(success=success)


@hotels_router.delete(
    '/my/favourites/{hotel_id}',
    status_code=status.HTTP_200_OK,
    response_model=SuccessModel,
)
async def remove_favourite_hotel(
        hotel_id: int,
        hotel_service: Annotated[HotelService, Depends(get_hotel_service)],
        user: Annotated[User, Depends(get_current_user)],
):
    await hotel_service.remove_favourite_hotel(user.id, hotel_id)
    return SuccessModel(success=True)
