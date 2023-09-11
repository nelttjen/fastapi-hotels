from sqladmin.models import ModelView

from src.users.models import User


class UserAdminView(ModelView, model=User):
    name = 'User'
    name_plural = 'Users'
    column_list = [User.id, User.username, User.email, User.is_active]
    column_details_list = [User.id, User.username, User.email, User.is_active]
    form_columns = [User.email, User.is_active]
    can_create = False
    can_delete = False
    can_export = False
    column_searchable_list = [User.username, User.password]
