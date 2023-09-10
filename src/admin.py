from sqladmin import Admin

from src.app import app
from src.database import engine
from src.middlewares import AdminAuthJWTMiddleware
from src.users.admin import UserAdminView

admin = Admin(app, engine, authentication_backend=AdminAuthJWTMiddleware('None'))

admin.add_view(UserAdminView)
