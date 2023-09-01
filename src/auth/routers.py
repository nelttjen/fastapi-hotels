from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.config import oauth2_scheme
from src.auth.dependencies import get_auth_service
from src.auth.schemas import RefreshToken, UserReadTokens
from src.auth.services import AuthService
from src.base.schemas import DetailModel
from src.users.schemas import UserCreate

auth_router = APIRouter(
    prefix='/auth',
)


@auth_router.post(
    path='/login',
    status_code=status.HTTP_201_CREATED,
    response_model=UserReadTokens,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Incorrect username or password',
        },
    },
)
async def token(
    auth_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await auth_service.authenticate_user(
        username=auth_credentials.username,
        password=auth_credentials.password,
    )


@auth_router.post(
    path='/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserReadTokens,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': DetailModel,
            'description': 'Bad register credentials',
        },
        status.HTTP_409_CONFLICT: {
            'model': DetailModel,
            'description': 'User with this username or password already exists',
        },
    },
)
async def register(
    user_create: UserCreate,
    user_service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await user_service.register_user(user_create)


@auth_router.post(
    path='/refresh',
    status_code=status.HTTP_200_OK,
    response_model=UserReadTokens,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Bad refresh token',
        },
    },
)
async def refresh(
    refresh_token: RefreshToken,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await auth_service.refresh_tokens(refresh_token.refresh_token)


@auth_router.post(
    path='/validate',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Bad access token',
        },
    },
)
async def validate(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    await auth_service.validate_access_token(access_token)
