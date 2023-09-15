from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action
from sqladmin.models import ModelView

from src.base.permissions import PermissionService
from src.database import context_db_session
from src.users.models import User


class UserAdminView(ModelView, model=User):
    name = 'User'
    name_plural = 'Users'
    column_list = [User.id, User.username, User.email, User.is_active, User.is_staff, User.is_superuser]
    column_details_list = [User.id, User.username, User.email, User.is_active, User.is_staff, User.is_superuser]
    form_columns = [User.email, User.is_active]
    can_create = False
    can_delete = False
    can_export = False
    column_searchable_list = [User.id, User.username, User.email]
    icon = 'fa-solid fa-user'

    @action(
        name='Promote to a staff',
        confirmation_message='Are you sure you want to promote this users to a staff users?',
        add_in_detail=True,
        add_in_list=True,
    )
    async def promote_to_staff(self, request: Request):
        pks = request.query_params.get('pks', '').split(',')
        if pks:
            with context_db_session() as session:
                perm_service = PermissionService(session=session)
                if not await perm_service.check_superuser(request):
                    return RedirectResponse(request.url_for('admin:list', identity=self.identity))

                # transaction = Transaction(session=session)
                # for pk in pks:
                #     model: User = await self.get_object_for_edit(pk)
                #     ...

        referer = request.headers.get('Referer')
        if referer:
            return RedirectResponse(referer)
        else:
            return RedirectResponse(request.url_for('admin:list', identity=self.identity))
