from sqladmin import Admin

from src.app import app
from src.bookings.admin import BookingAdminView
from src.database import engine
from src.hotels.admin import HotelAdminView, RoomAdminView
from src.middlewares import AdminAuthJWTMiddleware
from src.users.admin import UserAdminView

admin = Admin(app, engine, authentication_backend=AdminAuthJWTMiddleware('None'))

views = [UserAdminView, BookingAdminView, RoomAdminView, HotelAdminView]

for view in views:
    admin.add_view(view)
