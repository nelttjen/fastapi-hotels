from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from src.config import SECRET_KEY

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/login')

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 60 * 24 * 7

ACCESS_TOKEN_SECRET = SECRET_KEY + '_access'
REFRESH_TOKEN_SECRET = SECRET_KEY + '_refresh'

DISABLE_PASSWORD_VALIDATOR = True
