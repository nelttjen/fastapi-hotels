from enum import Enum
from typing import Annotated, Any, Callable, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


# https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types
class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:

        def validate_from_str(id_: str) -> ObjectId:
            return ObjectId(id_)

        from_str_schema = core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_plain_validator_function(validate_from_str),
        ])

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                from_str_schema,
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


PydanticObjectId = Annotated[
    ObjectId, _ObjectIdPydanticAnnotation,
]


class MongoModel(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias='_id', default=None)  # noqa

    class Meta:
        __collection__: str = None

    def to_document(self):
        document = self.model_dump()
        document.pop('id')

        for key, value in document.items():
            if isinstance(value, Enum):
                document[key] = value.value

        if self.id:
            document['_id'] = self.id

        return document
