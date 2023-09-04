from fastapi import APIRouter, Request

from src.pages import templates

front_bookings_router = APIRouter(
    prefix='/bookings',
    tags=['frontend'],
)


@front_bookings_router.get('/my')
async def my_bookings(request: Request):
    return templates.TemplateResponse('bookings/my.html', {'request': request})
