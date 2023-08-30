from typing import Any

from src.database import DatabaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, JSON


class Hotel(DatabaseModel):
    __tablename__ = 'hotel'

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, index=True,
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False,
    )
    location: Mapped[str] = mapped_column(
        String, nullable=False,
    )
    services: Mapped[dict[Any, Any]] = mapped_column(
        JSON, nullable=False, default=dict, server_default="'{}'",
    )
    rooms_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default='0',
    )
    image_id: Mapped[int] = mapped_column(
        Integer, nullable=True,
    )
