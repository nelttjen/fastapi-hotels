from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import Field
from pydantic_settings import BaseSettings

from src.config import app_settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/login')


class AuthSettings(BaseSettings):

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 30)  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 60 * 24 * 7)   # 7 days

    EMAIL_CODE_SEND_RATE_LIMIT: int = Field(default=60)  # 60 seconds
    EMAIL_CODE_EXPIRE_MINUTES: int = Field(default=60 * 30)   # 30 minutes

    ACCESS_TOKEN_SECRET: str = Field(default=app_settings.SECRET_KEY + '_access')
    REFRESH_TOKEN_SECRET: str = Field(default=app_settings.SECRET_KEY + '_refresh')

    DISABLE_PASSWORD_VALIDATOR: bool = Field(default=False)


auth_config = AuthSettings()
auth_config.DISABLE_PASSWORD_VALIDATOR = True
