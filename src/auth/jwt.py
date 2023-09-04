import datetime
from enum import Enum

from jose import jwt

from src.auth.config import (ACCESS_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_SECRET,
                             REFRESH_TOKEN_EXPIRE_MINUTES,
                             REFRESH_TOKEN_SECRET)
from src.users.models import User


class TokenType(str, Enum):
    ACCESS = 'access_token'
    REFRESH = 'refresh_token'


def _create_token(user: User, token_type: TokenType) -> str:
    minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    secret = ACCESS_TOKEN_SECRET
    if token_type == TokenType.REFRESH:
        minutes = REFRESH_TOKEN_EXPIRE_MINUTES
        secret = REFRESH_TOKEN_SECRET
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
