from pydantic import BaseModel, EmailStr

from src.users.schemas import UserRead


class UserReadTokens(BaseModel):
    user: UserRead
    access_token: str
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class EmailCodeRequestData(BaseModel):
    email: EmailStr


class RecoveryUserData(BaseModel):
    code: str
    new_password: str


class ActivateUserData(BaseModel):
    code: str
