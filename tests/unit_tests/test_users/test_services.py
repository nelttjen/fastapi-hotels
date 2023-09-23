import random
from typing import List

import pytest
from faker import Faker
from fastapi.exceptions import HTTPException
from sqlalchemy import select

from src.auth.config import auth_config
from src.users.exceptions import PasswordValidationError, UsernameOrEmailAlreadyExists, UsernameValidationError
from src.users.models import User
from src.users.schemas import UserUpdate
from src.users.services import RegisterService, UserService
from tests.conftest import override_settings


class TestUserCreateUpdate:
    @pytest.mark.parametrize(
        'username, email, password',
        [
            ('first_user', 'first_user@example.org', 'Weak_password123'),
            ('second_user', 'second_user@example.org', 'Secured_password123$#@098def4g$'),
        ],
    )
    async def test_create_user_success(self, user_service: UserService, username: str, email: str, password: str):
        res = await user_service.create_user(
            username=username,
            email=email,
            password=password,
        )
        assert res is not None
        assert res.username == username
        assert res.id is not None

        stmt = select(User).where(User.id == res.id)
        result = await user_service.repository.session.scalar(stmt)
        assert result is not None
        assert result.username == username

    @pytest.mark.parametrize(
        'password',
        [
            'short'
            'weak2',
            'weak_3',
            'password_without_numbers',
            'password0without0symbols',
            'to_long_0password_passsssssssssssssssssssssssssssssssssssssssssssssword',
        ],
    )
    async def test_create_user_password_fail(self, user_service: UserService, password: str):
        with pytest.raises(PasswordValidationError):
            await user_service.create_user(
                username='username_1',
                email='user_1@example.com',
                password=password,
                bypass_validation=False,
            )

    @pytest.mark.parametrize(
        'username, email, password',
        [
            ('user_1', 'user_1@example.com', 'Weak_password123'),
            ('user_2', 'user_2@example.com', 'Secured_password123$@098def4g$'),
        ],
    )
    async def test_create_user_password_ok(self, user_service: UserService, username: str, email: str, password: str):
        user = await user_service.create_user(
            username=username,
            email=email,
            password=password,
            bypass_validation=False,
        )

        stmt = select(User).where(User.username == username)
        result = await user_service.repository.session.scalar(stmt)
        assert result is not None
        assert result.username == username
        assert result.id == user.id

    @pytest.mark.parametrize(
        'username, email, password',
        [
            ('user_1', 'user_1@example.com', 'weak1'),
            ('user_2', 'user_2@example.com', 'w2'),
        ],
    )
    async def test_create_user_password_bypass(
            self, user_service: UserService, username: str, email: str, password: str,
    ):
        with pytest.raises(PasswordValidationError):
            await user_service.create_user(
                username=Faker().name(),
                email=Faker().email(),
                password=password,
                bypass_validation=True,
            )

    @pytest.mark.parametrize(
        'username',
        [
            'bad',
            'symbols$^&%*',
            'long_0000000000000000000000000000000000000000000000000',
        ],
    )
    async def test_create_user_username_fail(self, user_service: UserService, username: str):
        with pytest.raises(UsernameValidationError):
            await user_service.create_user(
                username=username,
                email=Faker().email(),
                password=Faker().password(),
                bypass_validation=False,
            )

    @pytest.mark.parametrize(
        'username, email, password',
        [
            ('user_1', 'user_1@example.com', 'user_1_123'),
            ('user_2', 'user_2@example.com', 'user_2@example.com123'),
        ],
    )
    async def test_password_validation_failure_contains(
            self, user_service: UserService, username: str, email: str, password: str,
    ):
        with pytest.raises(PasswordValidationError):
            await user_service.create_user(
                username=username,
                email=email,
                password=password,
                bypass_validation=False,
            )

    @pytest.mark.parametrize(
        'old_username, new_username',
        [
            ('user_1', 'new_user_1'),
            ('user_2', 'new_user_2'),
        ],
    )
    async def test_update_user_username_success(self, user_service: UserService, old_username: str, new_username: str):
        user = await user_service.create_user(
            username=old_username,
            email=Faker().email(),
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user is not None
        assert user.username == old_username
        assert user.id is not None

        res = await user_service.update_user(
            user=user,
            update_data=UserUpdate(username=new_username),
        )
        assert res is not None
        assert res.username == new_username
        assert res.id == user.id

        stmt = select(User).where(User.id == user.id)
        result = await user_service.repository.session.scalar(stmt)
        assert result is not None
        assert result.username == new_username

    @pytest.mark.parametrize(
        'old_username, new_username',
        [
            ('user_1', 'new_user_1'),
            ('user_2', 'new_user_2'),
        ],
    )
    async def test_update_user_username_already_exists(
            self, user_service: UserService, old_username: str, new_username: str,
    ):
        user = await user_service.create_user(
            username=old_username,
            email=Faker().email(),
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user is not None
        assert user.username == old_username
        assert user.id is not None

        user2 = await user_service.create_user(
            username=new_username,
            email=Faker().email(),
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user2 is not None
        assert user2.username == new_username
        assert user2.id is not None

        with pytest.raises(UsernameOrEmailAlreadyExists):
            await user_service.update_user(
                user=user2,
                update_data=UserUpdate(username=old_username),
            )

    @pytest.mark.parametrize(
        'old_email, new_email',
        [
            ('user_1@example.org', 'new_user_1@example.org'),
            ('user_2@example.org', 'new_user_2@example.org'),
        ],
    )
    async def test_update_user_email_success(self, user_service: UserService, old_email: str, new_email: str):
        user = await user_service.create_user(
            username=str(random.randint(1, 999999999999)),
            email=old_email,
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user is not None
        assert user.email == old_email
        assert user.id is not None

        res = await user_service.update_user(
            user=user,
            update_data=UserUpdate(email=new_email),
        )
        assert res is not None
        assert res.email == new_email
        assert res.id == user.id

        stmt = select(User).where(User.id == user.id)
        result = await user_service.repository.session.scalar(stmt)
        assert result is not None
        assert result.email == new_email

    @pytest.mark.parametrize(
        'old_email, new_email',
        [
            ('user_1@example.org', 'new_user_1@example.org'),
            ('user_2@example.org', 'new_user_2@example.org'),
        ],
    )
    async def test_update_user_email_already_exists(
            self, user_service: UserService, old_email: str, new_email: str,
    ):
        user = await user_service.create_user(
            username=str(random.randint(1, 999999999999)),
            email=old_email,
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user is not None
        assert user.email == old_email
        assert user.id is not None

        user2 = await user_service.create_user(
            username=str(random.randint(1, 999999999999)),
            email=new_email,
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user2 is not None
        assert user2.email == new_email
        assert user2.id is not None

        with pytest.raises(UsernameOrEmailAlreadyExists):
            await user_service.update_user(
                user=user2,
                update_data=UserUpdate(email=old_email),
            )

    @override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', True)
    async def test_update_user_password_success(self, user_service: UserService):
        old_pass = 'pwd1'
        new_pass = 'pwd2'
        user = await user_service.create_user(
            username=str(random.randint(1, 999999999999)),
            email=Faker().email(),
            password=old_pass,
            bypass_validation=True,
        )
        assert user.password is not None
        assert user.password != old_pass

        assert await RegisterService.check_password_hash(old_pass, str(user.password))

        updated_user = await user_service.update_user(
            user=user,
            update_data=UserUpdate(password=new_pass, old_password=old_pass),
        )

        assert updated_user.password is not None
        assert updated_user.password != new_pass
        assert updated_user.id == user.id
        assert not await RegisterService.check_password_hash(old_pass, str(updated_user.password))
        assert await RegisterService.check_password_hash(new_pass, str(updated_user.password))

    @override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', False)
    @pytest.mark.parametrize(
        'new_pass',
        [
            'bad', 'weak0', 'long_000000000000000000000000000000000000000000000000000000000000000000000000',
        ],
    )
    async def test_update_user_password_failure(self, user_service: UserService, new_pass: str):
        user = await user_service.create_user(
            username=str(random.randint(1, 99999999)),
            email=Faker().email(),
            password='test',
            bypass_validation=True,
        )
        assert user is not None

        with pytest.raises(PasswordValidationError):
            await user_service.update_user(
                user=user,
                update_data=UserUpdate(password=new_pass, old_password='test'),
            )

    @override_settings(auth_config, 'DISABLE_PASSWORD_VALIDATOR', True)
    async def test_update_user_password_old_missmatch(self, user_service: UserService):
        user = await user_service.create_user(
            username=str(random.randint(1, 999999999999)),
            email=Faker().email(),
            password='test',
            bypass_validation=True,
        )
        assert user is not None

        with pytest.raises(PasswordValidationError):
            await user_service.update_user(
                user=user,
                update_data=UserUpdate(password='new_pass', old_password='wrong_pass'),
            )


class TestUserService:
    @pytest.mark.parametrize(
        'username, email, query',
        [
            ('user_1', 'user_1@example.org', 'user_1'),
            ('user_2', 'user_2@example.org', 'user_2@example.org'),
        ],
    )
    async def test_find_user_for_login(self, user_service: UserService, username: str, email: str, query: str):
        user = await user_service.create_user(
            username=username,
            email=email,
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user is not None

        res = await user_service.get_user_for_login(query=query)
        assert res is not None
        assert res.username == username
        assert res.email == email
        assert res.id == user.id

    async def test_find_user_by_id(self, user_service: UserService):
        user = await user_service.create_user(
            username=str(random.randint(1, 999999999999)),
            email=Faker().email(),
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user is not None

        res = await user_service.get_user_by_id(user.id)
        assert res is not None
        assert res.username == user.username
        assert res.email == user.email
        assert res.id == user.id

    @pytest.mark.parametrize(
        'email',
        [
            'test1@example.org',
            'test2@example.org',
        ],
    )
    async def test_find_user_by_email(self, user_service: UserService, email):
        user = await user_service.create_user(
            username=str(random.randint(1, 999999999999)),
            email=email,
            password=Faker().password(),
            bypass_validation=True,
        )
        assert user is not None

        res = await user_service.get_user_by_email(email=email)
        assert res is not None
        assert res.username == user.username
        assert res.email == user.email
        assert res.id == user.id

    async def test_get_user_or_exception(self, user_service: UserService, users: List[User]):
        user = users[0]

        res = await user_service.get_user_or_401(user.id)
        res2 = await user_service.get_user_or_404(user.id)
        assert res is not None
        assert res2 is not None
        assert res.id == res2.id == user.id

        try:
            await user_service.get_user_or_401(-1111)
            raise AssertionError('Should have failed')
        except Exception as e:
            assert isinstance(e, HTTPException)
            assert e.status_code == 401

        try:
            await user_service.get_user_or_401(-1111, detail='test_detail')
            raise AssertionError('Should have failed')
        except Exception as e:
            assert isinstance(e, HTTPException)
            assert e.status_code == 401
            assert e.detail == 'test_detail'

        try:
            await user_service.get_user_or_404(-1111)
            raise AssertionError('Should have failed')
        except Exception as e:
            assert isinstance(e, HTTPException)
            assert e.status_code == 404
