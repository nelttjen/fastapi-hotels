from fastapi import APIRouter, Request

from src.pages import templates

front_hotels_router = APIRouter(
    prefix='/hotels',
    tags=['Frontend'],
)


@front_hotels_router.get('/search')
async def get_frontend_hotels(request: Request):
    return templates.TemplateResponse('hotels/search.html', {'request': request})


@front_hotels_router.get('/{hotel_id}/rooms')
async def get_frontend_rooms(request: Request, hotel_id: int):
    return templates.TemplateResponse('hotels/rooms.html', {'request': request, 'hotel_id': hotel_id})


@front_hotels_router.get('/favourites')
async def get_frontend_favourites(request: Request):
    return templates.TemplateResponse('hotels/favourites.html', {'request': request})
