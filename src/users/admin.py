from sqladmin.models import ModelView

from src.users.models import User


class UserAdminView(ModelView, model=User):
    column_list = '__all__'
