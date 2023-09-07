from typing import NoReturn


class NeverError(Exception):
    pass


def assert_never(*_: NoReturn, **__: NoReturn) -> NoReturn:
    raise NeverError('Values should never be called: %r, %r' % (_, __))