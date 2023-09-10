from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from src.pages import templates

front_bookings_router = APIRouter(
    prefix='/bookings',
    tags=['Frontend'],
)


@front_bookings_router.get('/my')
async def my_bookings(request: Request):
    return templates.TemplateResponse('bookings/my.html', {'request': request})


@front_bookings_router.get('/create')
async def create_booking(request: Request):
    if not (room_id := request.query_params.get('room_id')) or not (hotel_id := request.query_params.get('hotel_id')):
        return RedirectResponse('/hotels/search')
    return templates.TemplateResponse(
        'bookings/create.html',
        {'request': request, 'room_id': room_id, hotel_id: hotel_id},
    )
