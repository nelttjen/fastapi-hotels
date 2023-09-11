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


@front_auth_router.get('/email_code')
async def email_code(request: Request):
    request_type = request.query_params.get('request_type', '')
    if request_type not in ('activate', 'recovery'):
        return RedirectResponse(url='/auth/login')
    return templates.TemplateResponse('auth/email_code.html', {'request': request, 'request_type': request_type})


@front_auth_router.get('/recovery')
async def recovery(request: Request):
    if not (code := request.query_params.get('code', '')):
        return RedirectResponse(url='/auth/login')
    return templates.TemplateResponse('auth/recovery.html', {'request': request, 'code': code})


@front_auth_router.get('/activate')
async def activate(request: Request):
    if not (code := request.query_params.get('code', '')):
        return RedirectResponse(url='/auth/login')
    return templates.TemplateResponse('auth/activate.html', {'request': request, 'code': code})
