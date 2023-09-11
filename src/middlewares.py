from typing import Optional

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from src.auth.dependencies import get_auth_service, get_current_user
from src.database import context_db_session
from src.users.dependencies import get_user_service


class AdminAuthJWTMiddleware(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form['username'], form['password']
        async with context_db_session() as session:
            user_service = await get_user_service(session)
            auth_service = await get_auth_service(user_service)
            try:
                result = await auth_service.authenticate_user(username, password)
            except Exception:
                return False
            request.session['access_token'] = result['access_token']
            request.session['refresh_token'] = result['refresh_token']
        return True

    async def logout(self, request: Request) -> bool:
        try:
            del request.session['access_token']
            del request.session['refresh_token']
        except KeyError:
            ...
        return True

    @classmethod
    async def __check_user_access(cls, user) -> bool:
        # TODO: check if user is admin
        return user.is_active

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get('access_token')
        refresh_token = request.get('refresh_token')

        if not token:
            return RedirectResponse(request.url_for('admin:login'), status_code=status.HTTP_302_FOUND)

        async with context_db_session() as session:
            user_service = await get_user_service(session)
            auth_service = await get_auth_service(user_service)
            try:
                user = await get_current_user(auth_service, token)
                if not self.__check_user_access(user):
                    raise Exception
            except Exception:
                if refresh_token:
                    try:
                        data = await auth_service.refresh_tokens(refresh_token)
                        user = data['user']
                        if not self.__check_user_access(user):
                            raise Exception
                        request.session['access_token'] = data['access_token']
                        request.session['refresh_token'] = data['refresh_token']
                    except Exception:
                        return RedirectResponse(request.url_for('admin:login'), status_code=status.HTTP_302_FOUND)
                return RedirectResponse(request.url_for('admin:login'), status_code=status.HTTP_302_FOUND)
