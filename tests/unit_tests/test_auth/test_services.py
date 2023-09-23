import datetime
from typing import List

import pytest
from jose import JWTError

from src.auth.jwt import TokenType, create_access_token, create_refresh_token
from src.auth.services import AuthService
from src.users.models import User


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

    async def test_user_not_exists(self, auth_service: AuthService):
        pass


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
