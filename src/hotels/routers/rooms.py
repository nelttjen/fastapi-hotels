from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from src.hotels.dependencies import get_hotel_service
from src.hotels.schemas import DateRangeModel, HotelRoomDetailedInfo
from src.hotels.services import HotelService

rooms_router = APIRouter(
    prefix='/rooms',
)


@rooms_router.get(
    '/{hotel_id}/',
    status_code=status.HTTP_200_OK,
    response_model=List[HotelRoomDetailedInfo],
)
@cache(expire=60 * 30, namespace='clearable-get_rooms_for_hotel')
async def get_rooms_for_hotel(
        hotel_id: int,
        settings: Annotated[DateRangeModel, Depends()],
        hotel_service: Annotated[HotelService, Depends(get_hotel_service)],
):
    settings.validate_date_to()
    return await hotel_service.get_hotel_rooms(hotel_id, settings.date_from, settings.date_to)
