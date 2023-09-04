import logging

from src.config import config


class RequireDebugTrue(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa
        return config('DEBUG', False)


def init_loggers():
    try:
        logging.config.dictConfig(config('LOGGING', dict))
    except ValueError as e:
        logging.error(e)

    if config('DEBUG', False):
        debugger = logging.getLogger('debugger')
        debugger.debug('Loggers initialized')
