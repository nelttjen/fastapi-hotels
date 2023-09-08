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
            request.cookies['access_token'] = result['auth_token']
            request.cookies['refresh_token'] = result['refresh_token']
        return True

    async def logout(self, request: Request) -> bool:
        del request.cookies['refresh_token']
        del request.cookies['access_token']
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.cookies.get('access_token')

        if not token:
            return RedirectResponse(request.url_for('admin:login'), status_code=status.HTTP_302_FOUND)

        async with context_db_session() as session:
            user_service = await get_user_service(session)
            auth_service = await get_auth_service(user_service)
            try:
                await get_current_user(auth_service, token)
            except Exception:
                return RedirectResponse(request.url_for('admin:login'), status_code=status.HTTP_302_FOUND)

        # TODO: check if user is admin
