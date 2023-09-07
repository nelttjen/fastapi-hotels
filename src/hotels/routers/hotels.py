from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from src.base.schemas import DetailModel
from src.cache import KeyBuilderCache
from src.hotels.dependencies import get_hotel_service
from src.hotels.schemas import DateRangeModel, HotelInfo, HotelWithRoomsLeft
from src.hotels.services import HotelService

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
    '/c/test-del-cache',
)
async def test_del_cache():
    await KeyBuilderCache.clear_cache_for_func(search_available_hotels)
    return {'success': 'ok'}
