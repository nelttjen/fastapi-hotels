from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.config import app_settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/login')

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 60 * 24 * 7

ACCESS_TOKEN_SECRET = app_settings.SECRET_KEY + '_access'
REFRESH_TOKEN_SECRET = app_settings.SECRET_KEY + '_refresh'

EMAIL_CODE_EXPIRE_MINUTES = 30

DISABLE_PASSWORD_VALIDATOR = True
