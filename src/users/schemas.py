from typing import Optional

from pydantic import EmailStr, Field

from src.base.schemas import BaseORMModel


class UserBaseModel(BaseORMModel):
    username: str
    email: EmailStr


class UserCreate(UserBaseModel):
    password: str


class UserRead(UserBaseModel):
    id: int  # noqa


class UserUpdate(BaseORMModel):
    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    old_password: Optional[str] = Field(default=None)
