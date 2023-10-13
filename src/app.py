from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from migrations import __models__  # noqa
from src.auth.routers import auth_router
from src.bookings.routers import bookings_router
from src.cache import KeyBuilderCache, redis
from src.config import BASE_DIR, CORS_ALLOW_ORIGINS, app_settings
from src.database import context_db_session
from src.hotels.routers.hotels import hotels_router
from src.hotels.routers.rooms import rooms_router
from src.images.routers import image_router
from src.logging import init_loggers
from src.pages.auth import front_auth_router
from src.pages.bookings import front_bookings_router
from src.pages.hotels import front_hotels_router
from src.users.dependencies import get_user_service

app = FastAPI(debug=app_settings.DEBUG)

static_files = StaticFiles(directory=BASE_DIR / 'static')

app.mount('/static', static_files, 'static')

app.include_router(
    bookings_router,
    prefix='/api/v1',
    tags=['Bookings'],
)
app.include_router(
    auth_router,
    prefix='/api/v1',
    tags=['Auth'],
)
app.include_router(
    hotels_router,
    prefix='/api/v1',
    tags=['Hotels'],
)
app.include_router(
    rooms_router,
    prefix='/api/v1',
    tags=['Rooms'],
)

app.include_router(
    image_router,
    prefix='/api/v1',
    tags=['Images'],
)

app.include_router(
    front_auth_router,
    prefix='',
)
app.include_router(
    front_bookings_router,
    prefix='',
)
app.include_router(
    front_hotels_router,
    prefix='',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization', 'Set-Cookie',
                   'Accept-Control-Allow-Headers', 'Access-Authorization'],
)


@app.route('/')
async def root(*_, **__):
    return RedirectResponse('/hotels/search')


@app.on_event('startup')
async def startup_event():
    init_loggers()
    from src.admin import admin  # noqa

    FastAPICache.init(
        backend=RedisBackend(
            redis,
        ),
        prefix='fastapi-cache',
        key_builder=KeyBuilderCache.key_builder,
    )
    if app_settings.DEBUG:
        async with context_db_session() as session:
            service = await get_user_service(session)
            if not await service.get_user_for_login('admin'):
                user = await service.create_user(
                    username='admin',
                    email='admin@example.com',
                    password='admin',
                    bypass_validation=True,
                )
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                await session.merge(user)
                await session.commit()
