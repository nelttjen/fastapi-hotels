from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.config import app_settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/login')

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 60 * 24 * 7  # 7 days

EMAIL_CODE_SEND_RATE_LIMIT = 60  # 60 seconds
EMAIL_CODE_EXPIRE_MINUTES = 60 * 30  # 30 minutes

ACCESS_TOKEN_SECRET = app_settings.SECRET_KEY + '_access'
REFRESH_TOKEN_SECRET = app_settings.SECRET_KEY + '_refresh'


DISABLE_PASSWORD_VALIDATOR = True
