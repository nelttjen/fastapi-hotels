from sqladmin import Admin

from src.app import app
from src.config import app_settings
from src.database import engine
from src.middlewares import AdminAuthJWTMiddleware
from src.users.admin import UserAdminView

admin = Admin(app, engine=engine, debug=app_settings.DEBUG, authentication_backend=AdminAuthJWTMiddleware('None'))

admin.add_view(UserAdminView)
