import datetime
import logging
from dataclasses import dataclass
from typing import Any

from jose import JWTError, jwt

from src.auth.config import auth_config
from src.auth.exceptions import (
    BadCredentialsException,
    BadTokenException,
    EmailRateLimit,
    InvalidEmailCode,
    UserForEmailCodeNotFound,
    UserNotActiveException,
)
from src.auth.jwt import TokenType, create_tokens
from src.auth.models import CodeTypes, VerificationCode
from src.auth.repositories import EmailCodeSentRepository, VerificationCodeRepository
from src.auth.schemas import ActivateUserData, RecoveryUserData
from src.base.utils import get_utcnow
from src.celery_conf.tasks.emails import send_activation_email, send_recovery_email
from src.users.exceptions import PasswordValidationError
from src.users.models import User
from src.users.schemas import UserCreate
from src.users.services import RegisterService, UserService

debugger = logging.getLogger('debugger')


@dataclass
class AuthService:
    user_service: UserService
    verification_code_repository: VerificationCodeRepository
    email_code_repository: EmailCodeSentRepository

    @staticmethod
    def _parse_token(  # noqa: FNE008
            token: str, token_type: TokenType,
    ) -> dict:
        secret = auth_config.ACCESS_TOKEN_SECRET if token_type == TokenType.ACCESS else auth_config.REFRESH_TOKEN_SECRET

        payload = jwt.decode(
            token=token,
            key=secret,
            algorithms=['HS256'],
        )

        user_id = payload.get('user_id')
        username = payload.get('username')
        expires = payload.get('expires')
        token_type_payload = payload.get('token_type')

        if not all([user_id, username, expires, token_type_payload]):
            debugger.debug('bad payload')
            raise JWTError

        correct = token_type_payload == token_type.value
        expired = datetime.datetime.fromisoformat(expires) < get_utcnow()

        if not correct or expired:
            debugger.debug(f'{correct=} {expired=} {expires=}')
            raise JWTError

        return {
            'user_id': user_id,
            'username': username,
            'expires': expires,
            'token_type': token_type,
        }

    async def get_user_from_token(
            self, token: str, token_type: TokenType,
    ) -> User:
        data = self._parse_token(token=token, token_type=token_type)
        return await self.user_service.get_user_by_id(user_id=data['user_id'])

    async def authenticate_user(
        self, username: str, password: str,
    ) -> dict[str, Any]:
        user = await self.user_service.get_user_for_login(query=username)
        if not user:
            raise BadCredentialsException
        if not user.is_active:
            raise UserNotActiveException
        if not await RegisterService.check_password_hash(password, user.password):
            raise BadCredentialsException

        return {'user': user, **create_tokens(user)}

    async def refresh_tokens(
        self, refresh_token: str,
    ) -> dict[str, Any]:
        try:
            user = await self.get_user_from_token(refresh_token, TokenType.REFRESH)
            return {'user': user, **create_tokens(user)}
        except JWTError as exc:
            raise BadTokenException from exc

    async def validate_access_token(self, access_token: str):
        try:
            self._parse_token(access_token, TokenType.ACCESS)
        except JWTError as exc:
            raise BadTokenException from exc

    async def register_user(
        self, new_user: UserCreate,
    ) -> User:
        user = await self.user_service.create_user(
            username=new_user.username,
            email=new_user.email,
            password=new_user.password,
            bypass_validation=auth_config.DISABLE_PASSWORD_VALIDATOR,
        )
        await self.send_activation_email(new_user.email)
        return user

    async def _find_or_create_code(self, email: str, code_type: CodeTypes) -> VerificationCode:
        user = await self.user_service.get_user_by_email(email=email)
        if not user:
            raise UserForEmailCodeNotFound

        email_code_instance = await self.email_code_repository.get_email_rate_limit_model(email, code_type)

        if not email_code_instance.can_send_new_code(auth_config.EMAIL_CODE_SEND_RATE_LIMIT):
            raise EmailRateLimit

        await self.email_code_repository.update_last_sent(email_code_instance)

        code = await self.verification_code_repository.check_code_exists(user.id, code_type)
        if not code:
            code = await self.verification_code_repository.generate_verification_code(user.id, code_type)

        return code

    async def send_recovery_email(self, email: str) -> None:
        code = await self._find_or_create_code(email, CodeTypes.RECOVERY)
        send_recovery_email.delay(email=email, code=code.code)

    async def send_activation_email(self, email: str):
        code = await self._find_or_create_code(email, CodeTypes.ACTIVATION)
        send_activation_email.delay(email=email, code=code.code)

    async def recovery_user(self, recovery_data: RecoveryUserData):
        code = await self.verification_code_repository.get_valid_code(recovery_data.code)

        if not code or code.code_type != CodeTypes.RECOVERY:
            raise InvalidEmailCode
        user = await self.user_service.get_user_by_id(code.user_id)

        if await RegisterService.check_password_hash(recovery_data.new_password, user.password):
            raise PasswordValidationError('You cannot use your current password as the new password')
        if not auth_config.DISABLE_PASSWORD_VALIDATOR:
            await RegisterService.password_validator(user.username, user.email, recovery_data.new_password)

        user.password = await RegisterService.make_password_hash(recovery_data.new_password)
        await self.user_service.repository.update(user, commit=True)

        self.verification_code_repository.delete(code)

    async def activate_user(self, activate_data: ActivateUserData):
        code = await self.verification_code_repository.get_valid_code(activate_data.code)

        if not code or code.code_type != CodeTypes.ACTIVATION:
            raise InvalidEmailCode

        user = await self.user_service.get_user_by_id(code.user_id)
        user.is_active = True
        await self.user_service.repository.update(user, commit=True)

        self.verification_code_repository.delete(code)
