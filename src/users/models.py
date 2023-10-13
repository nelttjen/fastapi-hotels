from sqlalchemy import Boolean, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DatabaseModel


class User(DatabaseModel, AsyncAttrs):
    __tablename__ = 'user'
    __allow_unmapped__ = True

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
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default='FALSE',
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default='FALSE',
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default='FALSE',
    )

    bookings = relationship(
        'Booking', back_populates='user', lazy='select',
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        return f'id{self.id} {self.username}'
