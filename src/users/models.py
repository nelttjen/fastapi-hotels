from typing import List

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, JSON

from src.database import DatabaseModel


class User(DatabaseModel):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, index=True, autoincrement=True,
    )
    username: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True, index=True,
    )
    password: Mapped[str] = mapped_column(
        String(1024), nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=True,
    )
