from dataclasses import dataclass
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_auth_service
from src.auth.jwt import TokenType
from src.auth.services import AuthService
from src.users.dependencies import get_user_service


@dataclass
class PermissionService:
    session: Optional[AsyncSession]
    auth_service: Optional[AuthService] = None
    initialized: bool = False

    async def initialize_service(self):
        if self.initialized:
            return

        user_service = await get_user_service(self.session)
        self.auth_service = await get_auth_service(user_service)

    async def check_superuser(self, request: Request) -> bool:
        token = request.session.get('access_token')
        if not token:
            return False

        await self.initialize_service()
        user = await self.auth_service.get_user_from_token(token, TokenType.ACCESS)

        return user and user.is_superuser
