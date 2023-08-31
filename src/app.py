from typing import Literal

from fastapi import FastAPI
from src.bookings.routers import bookings_router
from migrations import __models__  # noqa

app = FastAPI()

app.include_router(
    bookings_router,
    prefix='/api/v1',
    tags=['Bookings'],
)
