from typing import Annotated

from fastapi import Depends
from jose import JWTError
from pymongo import MongoClient

from src.auth.config import oauth2_scheme
from src.auth.jwt import TokenType
from src.auth.repositories import EmailCodeSentRepository, VerificationCodeRepository
from src.auth.services import AuthService
from src.base.exceptions import Unauthorized
from src.config import mongo_settings
from src.users.dependencies import get_user_service
from src.users.models import User
from src.users.services import UserService


async def get_auth_service(
        user_service: Annotated[UserService, Depends(get_user_service)],
) -> AuthService:
    mongo_session = MongoClient(**mongo_settings.MONGODB_AUTHPARAMS).get_database(mongo_settings.MONGODB_DB)
    verification_code_repository = VerificationCodeRepository(database=mongo_session)
    email_code_repository = EmailCodeSentRepository(database=mongo_session)
    return AuthService(user_service, verification_code_repository, email_code_repository)


async def get_current_user(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        access_token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        return await auth_service.get_user_from_token(access_token, TokenType.ACCESS)
    except JWTError as exc:
        raise Unauthorized('Token expired') from exc
