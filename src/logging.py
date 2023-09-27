import logging

from src.config import app_settings, config


class RequireDebugTrue(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa
        return app_settings.DEBUG


def init_loggers():
    try:
        logging.config.dictConfig(config('LOGGING', dict))  # noqa
        debugger = logging.getLogger('debugger')
        debugger.debug('Loggers initialized')
    except ValueError as e:
        logging.error(e)
