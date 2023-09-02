from typing import Generic, TypeVar
from dataclasses import dataclass
from abc import ABC

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import DatabaseModel

T = TypeVar('T', bound=DatabaseModel)


@dataclass
class BaseRepository(ABC, Generic[T]):
    session: AsyncSession

    async def create(self, model: T, commit: bool = False) -> T:
        self.session.add(model)
        if commit:
            await self.commit()
        return model

    async def bulk_create(self, models: list[T], commit: bool = False) -> list[T]:
        self.session.add_all(models)
        if commit:
            await self.commit()
        return models

    async def update(self, model: T, commit: bool = False) -> T:
        await self.session.merge(model)
        if commit:
            await self.commit()
        return model

    async def delete(self, model: T, commit: bool = False) -> None:
        await self.session.delete(model)
        if commit:
            await self.commit()
        return model

    async def flush(self) -> None:
        await self.session.flush()

    async def refresh(self, model: T) -> None:
        await self.session.refresh(model)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


@dataclass
class Transaction:
    session: AsyncSession

    async def __aenter__(self):
        if self.session is None:
            raise RuntimeError('Session is not initialized')
        try:
            await self.session.begin()
        except InvalidRequestError:
            """Transaction already has begun"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
            return

        await self.session.commit()
