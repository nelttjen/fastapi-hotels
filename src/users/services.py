import re
from dataclasses import dataclass
from typing import Optional, Type

from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from src.auth.config import pwd_context
from src.base.exceptions import HTTP_EXC, NotFound, Unauthorized
from src.base.repositories import Transaction
from src.config import config
from src.users.exceptions import (
    PasswordValidationError,
    UsernameOrEmailAlreadyExists,
    UsernameValidationError,
)
from src.users.models import User
from src.users.repositories import UserRepository
from src.users.schemas import UserUpdate


@dataclass
class UserService:
    repository: UserRepository
    transaction: Transaction

    async def create_user(
            self,
            username: str,
            email: EmailStr,
            password: str,
    ) -> User:
        async with self.transaction:
            await self.repository.credentials_available(email=email, username=username)

            await RegisterService.password_validator(username=username, email=email, password=password)
            await RegisterService.username_validator(username=username)

            hashed_password = await RegisterService.make_password_hash(password=password)

            user = User(
                username=username,
                email=email,
                password=hashed_password,
            )
            await self.repository.create(user)

        return user

    async def update_user(
            self,
            user: User,
            update_data: UserUpdate,
    ):
        if update_data.username:
            await RegisterService.username_validator(username=update_data.username)
            user.username = update_data.username

        if update_data.email:
            user.email = update_data.email

        if update_data.password and update_data.old_password:
            if not await RegisterService.check_password_hash(update_data.old_password, user.password):
                raise PasswordValidationError('Old password does not match')

            await RegisterService.password_validator(
                username=user.username, email=user.email, password=update_data.password,
            )
            user.password = await RegisterService.make_password_hash(password=update_data.password)

        try:
            async with self.transaction:
                await self.repository.update(user)
        except IntegrityError as e:
            raise UsernameOrEmailAlreadyExists('username or email already exists') from e

        return user

    async def get_user_for_login(self, query: str) -> User | None:
        return await self.repository.find_for_login(search=query)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_by_id(user_id=user_id)

    async def _get_user_or_exception(
            self, user_id: int, exception: Type[HTTP_EXC], detail: Optional[str] = None,
    ) -> User | None:
        user = await self.get_user_by_id(user_id=user_id)

        if not user:
            if detail:
                exception = exception(detail)

            raise exception

        return user

    async def get_user_or_401(
            self, user_id: int, detail: Optional[str] = None,
    ) -> User:
        return await self._get_user_or_exception(user_id, Unauthorized, detail)

    async def get_user_or_404(
            self, user_id: int, detail: Optional[str] = None,
    ) -> User:
        return await self._get_user_or_exception(user_id, NotFound, detail)


class RegisterService:

    @staticmethod
    async def password_validator(
            username: str, email: str, password: str,
    ) -> None:
        if config('DISABLE_PASSWORD_VALIDATOR', False, module='src.auth.config'):
            return

        if username in password or email in password:
            raise PasswordValidationError('Password cannot contains username or email')

        if not 6 <= len(password) <= 50:
            raise PasswordValidationError('Password must be between 6 and 50 characters long')

        regex_password = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[\d#@$=_+*&^%]).+$')
        if not regex_password.match(password):
            raise PasswordValidationError('Password must contain at least one uppercase letter, lower case letter, '
                                          'and at least one number or special character (#@$=_+*&^%)')

    @staticmethod
    async def username_validator(username: str) -> None:
        regex_username = re.compile(r'^[a-zA-Z0-9_-]{4,32}$')
        if not regex_username.match(username):
            raise UsernameValidationError('Username must be between 4 and 32 characters long, '
                                          'and can contain only letters, numbers and dashes')

    @staticmethod
    async def make_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def check_password_hash(
            plain_password: str, hashed_password: str,
    ) -> bool:
        return pwd_context.verify(plain_password, hashed_password)