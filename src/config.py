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

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


db_settings = DatabaseSettings()

DEBUG = True
ENABLE_QUERY_DEBUGGING = True
SECRET_KEY = os.getenv('SECRET_KEY')

CORS_ALLOW_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1',
]

CONNECTION_PROTOCOL = 'http'
DOMAIN = '127.0.0.1:8000'


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
