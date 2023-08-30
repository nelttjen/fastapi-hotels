import importlib
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

info = logging.getLogger('all')

BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEBUG = True
ENABLE_QUERY_DEBUGGING = True

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY')

DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')

DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

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


@lru_cache(maxsize=20, typed=True)
def config(value: Any, default: Any = None, module: str = 'src.config') -> Any:
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
