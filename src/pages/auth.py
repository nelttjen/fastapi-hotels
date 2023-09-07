from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from src.pages import templates

front_auth_router = APIRouter(
    prefix='/auth',
    tags=['Frontend'],
)


@front_auth_router.get('/login')
async def login(request: Request):
    return templates.TemplateResponse('auth/login.html', {'request': request})


@front_auth_router.get('/register')
async def register(request: Request):
    return templates.TemplateResponse('auth/register.html', {'request': request})


@front_auth_router.get('/logout')
async def logout():
    response = RedirectResponse(url='/auth/login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('user')
    return response
