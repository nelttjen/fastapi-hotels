from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, Iterable, Optional, Tuple, Type, TypeVar

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.exceptions import HTTP_EXC, InternalServerError
from src.base.models import MongoModel
from src.database import DatabaseModel

T = TypeVar('T', bound=DatabaseModel)
MT = TypeVar('MT', bound=MongoModel)

Sort = Sequence[Tuple[str, int]]


@dataclass
class BaseRepository(ABC, Generic[T]):
    session: AsyncSession
    bind_model: Optional[Type[T]] = None

    async def _get_or_exception(
            self, model_id: int, exception: Type[HTTP_EXC], detail: Optional[str] = None,
    ) -> bind_model:
        if not self.bind_model:
            raise InternalServerError('Model is not binded to repository')

        model = await self.session.get(self.bind_model, model_id)
        if model is None:
            raise exception(detail=detail)
        return model

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
            """Transaction already has begun."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
            return

        await self.session.commit()


@dataclass
class AbstractMongoRepository(ABC, Generic[MT]):
    database: Database

    class Meta:
        bind_model: Type[MT]

    def get_collection(self) -> Collection:
        if self.database is None:
            raise RuntimeError('Database is not initialized')
        if self.Meta.bind_model is None:
            raise RuntimeError('Model is not binded to repository in Meta class')
        if self.Meta.bind_model.Meta.__collection__ is None:
            raise RuntimeError(f'Collection is not defined in Meta class in model {self.Meta.bind_model.__name__}')
        return self.database.get_collection(self.Meta.bind_model.Meta.__collection__)

    @staticmethod
    def _check_object_id(_id: ObjectId | str) -> ObjectId:
        if not isinstance(_id, ObjectId) and not ObjectId.is_valid(_id):
            raise ValueError(f'Invalid ObjectId: {_id}')
        return ObjectId(_id)

    @staticmethod
    def __map_only(seq: list) -> dict[str, bool]:
        only = {'_id': False}
        for value in seq:
            only[value] = True
        return only

    def save(self, model: MT) -> InsertOneResult | UpdateResult:  # noqa
        """Save entity to database.

        It will update the entity if it has id, otherwise it will insert
        it.
        """
        document = model.to_document()

        if model.id:
            mongo_id = document.pop('_id')
            return self.get_collection().update_one(
                {'_id': mongo_id}, {'$set': document},
            )

        result = self.get_collection().insert_one(document)
        model.id = result.inserted_id
        return result

    def delete(self, model: MT) -> DeleteResult | None:
        """Delete entity from database."""
        if not model.id:
            return None
        return self.get_collection().delete_one({'_id': model.id})

    def find_one_by_id(self, _id: ObjectId | str) -> MT | None:
        _id = self._check_object_id(_id)

        return self.find_one(_id=_id)

    def find_one(self, **kwargs) -> MT | None:
        result = self.get_collection().find_one(kwargs)
        if not result:
            return
        validated = self.Meta.bind_model.model_validate(result)
        return validated

    def find_all(
            self,
            query: dict,
            skip: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[Sort] = None,
            only: Optional[list[str]] = None,
    ) -> Iterable[MT]:
        if only is not None:
            only = self.__map_only(only)

        cursor = self.get_collection().find(query, only)

        if limit:
            cursor.limit(limit)
        if skip:
            cursor.skip(skip)
        if sort:
            cursor.sort(sort)

        return map(lambda x: self.Meta.bind_model.model_validate(x), cursor)
