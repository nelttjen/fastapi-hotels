from pydantic import BaseModel

from src.users.schemas import UserRead


class UserReadTokens(BaseModel):
    user: UserRead
    access_token: str
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str
