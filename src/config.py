import importlib
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(BASE_DIR / '.env')


_base_env_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:  # noqa
        return (f'postgresql+asyncpg://'
                f'{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/'
                f'{self.POSTGRES_DB}')

    model_config = _base_env_config.copy()


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def REDIS_URL(self) -> str:  # noqa
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    @property
    def CELERY_BROKER_URL(self) -> str:  # noqa
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1'

    @property
    def CELERY_RESULT_BACKEND(self) -> str:  # noqa
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2'

    model_config = _base_env_config.copy()


class MongoSettings(BaseSettings):
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_DB: str

    @property
    def MONGODB_AUTHPARAMS(self) -> dict[str, Any]:  # noqa
        return {
            'host': self.MONGODB_HOST,
            'port': self.MONGODB_PORT,
            'username': self.MONGODB_USER,
            'password': self.MONGODB_PASSWORD,
            'authSource': self.MONGODB_DB,
        }

    model_config = _base_env_config.copy()


class SMTPSettings(BaseSettings):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    model_config = _base_env_config.copy()


class AppSettings(BaseSettings):
    DEBUG: bool
    ENABLE_QUERY_DEBUGGING: bool
    SECRET_KEY: str

    model_config = _base_env_config.copy()


db_settings = DatabaseSettings()
redis_settings = RedisSettings()
mongo_settings = MongoSettings()
google_smtp_settings = SMTPSettings()
app_settings = AppSettings()

CORS_ALLOW_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1',
]

CONNECTION_PROTOCOL = 'http'
DOMAIN = '127.0.0.1:8000'
IMAGES_URL = Path('/static/images')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'filters': {
        'debug_only': {
            '()': 'src.logging.RequireDebugTrue',
        },
    },

    'formatters': {
        'json_formatter': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(process)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)s %(message)s)',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'console_formatter': {
            'format': '[{levelname}] ({asctime} - {module}) ({filename}:{lineno} - {funcName}): {message}',
            'datefmt': '%H:%M:%S',
            'style': '{',
        },
        'debugger': {
            'format': '[{levelname}]: {message}',
            'style': '{',
        },

        'file_formatter': {
            'format': '[{levelname}] ({asctime} - {module} (PID: {process:d}, THREAD: {thread:d})): {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['debug_only'],
            'formatter': 'console_formatter',
            'level': 'DEBUG',
        },
        'debugger': {
            'class': 'logging.StreamHandler',
            'filters': ['debug_only'],
            'formatter': 'debugger',
            'level': 'DEBUG',
        },
        'info': {
            'class': 'logging.FileHandler',
            'formatter': 'file_formatter',
            'filename': os.path.join(BASE_DIR, 'logs', 'info.log'),
            'level': 'INFO',
        },
        'error': {
            'class': 'logging.FileHandler',
            'formatter': 'file_formatter',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'level': 'ERROR',
        },
        'info_json': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': os.path.join(BASE_DIR, 'logs', 'info_json.log'),
            'level': 'INFO',
        },
        'error_json': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': os.path.join(BASE_DIR, 'logs', 'error_json.log'),
            'level': 'ERROR',
        },
    },
    'loggers': {
        'debugger': {
            'handlers': ['debugger'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'all': {
            'handlers': ['console', 'info', 'error', 'info_json', 'error_json'],
            'level': 'DEBUG',
        },
    },
}


@lru_cache(maxsize=50, typed=True)
def config(value: Any, default: Any = None, module: str = 'src.config') -> Any:
    info = logging.getLogger('all')
    try:
        module = importlib.import_module(module)
    except ModuleNotFoundError:
        info.warning(f'Module {module} not found while calling config func')
        if callable(default):
            return default()
        return default

    if hasattr(module, value):
        return getattr(module, value)

    if callable(default):
        return default()
    return default
