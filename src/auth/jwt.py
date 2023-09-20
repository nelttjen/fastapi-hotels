import datetime
from enum import Enum

from jose import jwt

from src.auth.config import auth_config
from src.users.models import User


class TokenType(str, Enum):
    ACCESS = 'access_token'
    REFRESH = 'refresh_token'


def _create_token(user: User, token_type: TokenType) -> str:
    minutes = auth_config.ACCESS_TOKEN_EXPIRE_MINUTES
    secret = auth_config.ACCESS_TOKEN_SECRET
    if token_type == TokenType.REFRESH:
        minutes = auth_config.REFRESH_TOKEN_EXPIRE_MINUTES
        secret = auth_config.REFRESH_TOKEN_SECRET
    expires = (datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)).isoformat()

    data = {
        'user_id': user.id,
        'username': user.username,
        'token_type': token_type,
        'expires': expires,
    }

    return jwt.encode(data, key=secret, algorithm='HS256')


def create_access_token(user: User) -> str:
    return _create_token(user, TokenType.ACCESS)


def create_refresh_token(user: User) -> str:
    return _create_token(user, TokenType.REFRESH)


def create_tokens(user: User) -> dict[str, str]:
    access = create_access_token(user)
    refresh = create_refresh_token(user)

    return {
        TokenType.ACCESS.value: access,
        TokenType.REFRESH.value: refresh,
    }
