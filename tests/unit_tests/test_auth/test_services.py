import datetime
from typing import List

import pytest
from jose import JWTError
from pymongo.database import Database
from sqlalchemy import select

from src.auth.config import auth_config
from src.auth.exceptions import (BadCredentialsException, BadTokenException, EmailRateLimit, InvalidEmailCode,
                                 UserForEmailCodeNotFound, UserNotActiveException)
from src.auth.jwt import TokenType, create_access_token, create_refresh_token
from src.auth.models import CodeTypes, EmailCodeSent
from src.auth.schemas import ActivateUserData, RecoveryUserData
from src.auth.services import AuthService
from src.users.exceptions import PasswordValidationError
from src.users.models import User
from src.users.schemas import UserCreate
from src.users.services import RegisterService
from tests.conftest import override_settings


class TestAuthService:
    @pytest.mark.parametrize(
        'username, password, email',
        [
            ('user_1', 'user_1_password', 'lyhxr@example.com'),
            ('user_2', 'user_2_password', 'lyhxr2@example.com'),
        ],
    )
    async def test_user_login(self, auth_service: AuthService, username, password, email):
        user = await auth_service.user_service.create_user(
            username=username,
            password=password,
            email=email,
            bypass_validation=True,
        )

        assert user is not None

        user.is_active = True
        await auth_service.user_service.repository.update(user, commit=True)

        result = await auth_service.authenticate_user(username=username, password=password)

        assert result is not None
        assert result.get('user').username == username
        assert result.get('access_token') is not None
        assert result.get('refresh_token') is not None

    async def test_token_decode_user_not_exists(self, auth_service: AuthService):
        fake_user = User(
            id=999,
            username='fake_user',
            password='<PASSWORD>',
            email='<EMAIL>',
            is_active=True,
        )
        token = create_access_token(fake_user)

        assert token is not None
        user = await auth_service.get_user_from_token(token, TokenType.ACCESS)
        assert user is None

    async def test_login_user_not_exists(self, auth_service: AuthService):
        username = 'fake_user_sdfs'
        password = 'fake_password'
        stmt = select(User).where(User.username.ilike(f'{username}'))
        user = await auth_service.user_service.repository.session.scalar(stmt)
        assert user is None

        with pytest.raises(BadCredentialsException):
            await auth_service.authenticate_user(username=username, password=password)

    @override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', True)
    async def test_user_not_active(self, auth_service: AuthService, mocker):
        mocker.patch('src.auth.services.AuthService.send_activation_email', return_value=None)

        create = UserCreate(username='fake_user', password='fake_password', email='lyhxr@example.com')
        user = await auth_service.register_user(create)

        assert user.username == 'fake_user'
        assert user.is_active is False

        with pytest.raises(UserNotActiveException):
            await auth_service.authenticate_user(username='fake_user', password='fake_password')

    @override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', True)
    async def test_user_password_incorrect(self, auth_service: AuthService, mocker):
        mocker.patch('src.auth.services.AuthService.send_activation_email', return_value=None)
        create = UserCreate(username='fake_user', password='fake_password', email='lyhxr@example.com')

        user = await auth_service.register_user(create)
        assert user.username == 'fake_user'

        user.is_active = True
        await auth_service.user_service.repository.update(user, commit=True)

        good_creds_user = await auth_service.authenticate_user(username='fake_user', password='fake_password')

        assert good_creds_user.get('user').username == 'fake_user'
        assert good_creds_user.get('access_token') is not None

        with pytest.raises(BadCredentialsException):
            await auth_service.authenticate_user(username='fake_user', password='bad_password')


class TestJWTTokens:
    async def test_token_types(self, auth_service: AuthService, users: List[User]):
        user = users[0]
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)

        async def token_test(token: str, token_type: TokenType, wrong_token_type: TokenType):
            decoded_user = await auth_service.get_user_from_token(token, token_type)
            assert decoded_user.id == user.id

            with pytest.raises(JWTError):
                _ = await auth_service.get_user_from_token(token, wrong_token_type)

        await token_test(access_token, TokenType.ACCESS, TokenType.REFRESH)
        await token_test(refresh_token, TokenType.REFRESH, TokenType.ACCESS)

    async def test_token_expiration(self, mocker, auth_service: AuthService, users: List[User]):
        user = users[0]

        mocker.patch('src.auth.jwt.get_utcnow', return_value=datetime.datetime(year=1970, month=1, day=1))

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)

        with pytest.raises(JWTError):
            _ = await auth_service.get_user_from_token(access_token, TokenType.ACCESS)

        with pytest.raises(JWTError):
            _ = await auth_service.get_user_from_token(refresh_token, TokenType.REFRESH)

    async def test_refresh_tokens_success(self, auth_service: AuthService, users: List[User]):
        user = users[0]

        assert user is not None

        refresh_token = create_refresh_token(user)
        assert isinstance(refresh_token, str)

        refreshed = await auth_service.refresh_tokens(refresh_token)

        assert refreshed is not None
        assert refreshed.get('user').username == user.username
        assert refreshed.get('access_token') is not None
        assert refreshed.get('refresh_token') is not None
        assert refreshed.get('refresh_token') != refresh_token

    async def test_refresh_tokens_wrong_type(self, auth_service: AuthService, users: List[User]):
        user = users[0]

        assert user is not None

        access_token = create_access_token(user)
        assert isinstance(access_token, str)

        with pytest.raises(BadTokenException):
            await auth_service.refresh_tokens(access_token)

        await auth_service.validate_access_token(access_token)

    async def test_refresh_tokens_expired(self, auth_service: AuthService, users: List[User], mocker):
        user = users[0]

        assert user is not None

        mocker.patch('src.auth.jwt.get_utcnow', return_value=datetime.datetime(year=1970, month=1, day=1))

        refresh_token = create_refresh_token(user)
        assert isinstance(refresh_token, str)

        mocker.patch('src.auth.jwt.get_utcnow', return_value=datetime.datetime.utcnow())

        with pytest.raises(BadTokenException):
            await auth_service.refresh_tokens(refresh_token)

    async def test_validate_access_token_success(self, auth_service: AuthService, users: List[User]):
        user = users[0]

        access_token = create_access_token(user)
        assert isinstance(access_token, str)

        await auth_service.validate_access_token(access_token)

    async def test_validate_access_token_error_expired(self, auth_service: AuthService, users: List[User], mocker):
        user = users[0]

        assert user is not None

        mocker.patch('src.auth.jwt.get_utcnow', return_value=datetime.datetime(year=1970, month=1, day=1))

        access_token = create_access_token(user)
        assert isinstance(access_token, str)

        mocker.patch('src.auth.jwt.get_utcnow', return_value=datetime.datetime.utcnow())

        with pytest.raises(BadTokenException):
            await auth_service.validate_access_token(access_token)


class TestVerificationCode:

    async def test_verification_code_wrong_email(self, auth_service: AuthService):
        with pytest.raises(UserForEmailCodeNotFound):
            await auth_service._find_or_create_code('wrong@email.com', CodeTypes.ACTIVATION)

    async def test_verification_code_success(self, auth_service: AuthService, fake_user: User):
        code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)

        assert code is not None
        assert code.code_type == CodeTypes.ACTIVATION
        assert code.code is not None
        assert code.expires is not None
        assert datetime.datetime.fromtimestamp(code.expires) > datetime.datetime.utcnow()
        assert code.user_id == fake_user.id

    async def test_verification_code_email_rate_limit(self, auth_service: AuthService, fake_user: User):
        code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)

        assert code is not None

        with pytest.raises(EmailRateLimit):
            await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)

        assert len(list(auth_service.verification_code_repository.find_all({'user_id': fake_user.id}))) == 1

    async def test_verification_code_no_duplicates(
            self, auth_service: AuthService, fake_user: User, mongo_session: Database,
    ):
        code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)
        mongo_session.get_collection(EmailCodeSent.Meta.__collection__).delete_many({
            'email': fake_user.email,
        })
        second_code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)

        assert code.code == second_code.code
        assert code.code_type == second_code.code_type == CodeTypes.ACTIVATION

    async def test_verification_code_types(self, auth_service: AuthService, fake_user: User):
        activation_code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)
        recovery_code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.RECOVERY)

        assert activation_code.code_type == CodeTypes.ACTIVATION
        assert recovery_code.code_type == CodeTypes.RECOVERY
        assert activation_code.code != recovery_code.code

        assert len(list(auth_service.email_code_repository.find_all({'email': fake_user.email}))) == 2

    async def test_activate_user_success(self, auth_service: AuthService, fake_user: User):
        activation_code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)

        assert activation_code.code is not None

        fake_user.is_active = False
        await auth_service.user_service.repository.update(fake_user, commit=True)

        await auth_service.activate_user(ActivateUserData(
            code=activation_code.code,
        ))

        stmt = select(User).where(User.email == fake_user.email)
        user = await auth_service.user_service.repository.session.scalar(stmt)

        assert user.id == fake_user.id
        assert user.is_active is True

    async def test_activate_user_invalid_activation_code(self, auth_service: AuthService, fake_user: User):

        fake_user.is_active = False
        await auth_service.user_service.repository.update(fake_user, commit=True)

        with pytest.raises(InvalidEmailCode):
            await auth_service.activate_user(ActivateUserData(
                code='wrong_code',
            ))

        stmt = select(User).where(User.email == fake_user.email)
        user = await auth_service.user_service.repository.session.scalar(stmt)
        assert user.id == fake_user.id
        assert user.is_active is False

    async def test_activate_user_code_expired(self, auth_service: AuthService, fake_user: User, mocker):
        mocker.patch('src.auth.repositories.get_utcnow', return_value=datetime.datetime(year=1970, month=1, day=1))

        code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.ACTIVATION)

        fake_user.is_active = False
        await auth_service.user_service.repository.update(fake_user, commit=True)

        mocker.patch('src.auth.repositories.get_utcnow', return_value=datetime.datetime.utcnow())

        with pytest.raises(InvalidEmailCode):
            await auth_service.activate_user(ActivateUserData(
                code=code.code,
            ))

        stmt = select(User).where(User.email == fake_user.email)
        user = await auth_service.user_service.repository.session.scalar(stmt)
        assert user.id == fake_user.id
        assert user.is_active is False

    async def test_activate_user_code_wrong_type(self, auth_service: AuthService, fake_user: User):
        code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.RECOVERY)

        fake_user.is_active = False
        await auth_service.user_service.repository.update(fake_user, commit=True)

        with pytest.raises(InvalidEmailCode):
            await auth_service.activate_user(ActivateUserData(
                code=code.code,
            ))

        stmt = select(User).where(User.email == fake_user.email)
        user = await auth_service.user_service.repository.session.scalar(stmt)
        assert user.is_active is False
        assert user.id == fake_user.id

    @override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', True)
    async def test_recovery_user_success(self, auth_service: AuthService, fake_user: User):
        code = await auth_service._find_or_create_code(fake_user.email, CodeTypes.RECOVERY)

        new_pass = 'new_pass'
        password_hash_before = fake_user.password
        data = RecoveryUserData(
            code=code.code,
            new_password=new_pass,
        )

        await auth_service.recovery_user(data)

        stmt = select(User).where(User.email == fake_user.email)
        user = await auth_service.user_service.repository.session.scalar(stmt)

        assert user.id == fake_user.id

        assert await RegisterService.check_password_hash(new_pass, user.password)
        assert not await RegisterService.check_password_hash(new_pass, password_hash_before)

        assert len(list(auth_service.verification_code_repository.find_all({'user_id': fake_user.id}))) == 0

    async def test_recovery_user_same_password(self, auth_service: AuthService):
        new_pass = 'password'

        user = await auth_service.user_service.create_user(
            username='test',
            email='efpyi@example.com',
            password=new_pass,
            bypass_validation=True,
        )

        code = await auth_service._find_or_create_code(user.email, CodeTypes.RECOVERY)

        data = RecoveryUserData(
            code=code.code,
            new_password=new_pass,
        )

        with pytest.raises(PasswordValidationError):
            await auth_service.recovery_user(data)

        assert await RegisterService.check_password_hash(new_pass, user.password)
