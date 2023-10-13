import pytest
from httpx import AsyncClient
from fastapi import status

from tests.conftest import override_settings
from src.auth.config import auth_config


class TestAuth:

    @pytest.mark.disable_clean
    @pytest.mark.parametrize(
        'username, email, password, expected_status',
        [
            ('tester', 'tester@example.com', 'tester', status.HTTP_201_CREATED),
            ('tester', 'tester2@example.com', 'tester', status.HTTP_409_CONFLICT),
            ('tester2', 'tester@example.com', 'tester', status.HTTP_409_CONFLICT),
            ('tester2', 'tester2@example.com', 'tester', status.HTTP_201_CREATED),
        ],
    )
    @override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', True)
    async def test_register(self, ac: AsyncClient, username, email, password, expected_status):
        response = await ac.post('/api/v1/auth/register', json={
            'username': username,
            'email': email,
            'password': password,
        })
        assert response.status_code == expected_status
