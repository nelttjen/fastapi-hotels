import pytest

from tests.conftest import override_settings
from src.auth.config import auth_config


@pytest.mark.parametrize(
    'test',
    [
        ('first',),
        ('second',),
    ],
)
@override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', False)
async def test_override_1(test):
    assert auth_config.DISABLE_PASSWORD_VALIDATOR is False


@pytest.mark.parametrize(
    'test',
    [
        ('first',),
        ('second',),
    ],
)
@override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', True)
async def test_override_2(test):
    assert auth_config.DISABLE_PASSWORD_VALIDATOR is True
