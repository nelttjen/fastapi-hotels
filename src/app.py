from fastapi import FastAPI

from migrations import __models__  # noqa
from src.bookings.routers import bookings_router
from src.auth.routers import auth_router
from src.logging import init_loggers

init_loggers()

app = FastAPI()

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