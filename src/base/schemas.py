from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class BaseORMModel(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class SuccessModel(BaseModel):
    success: bool = Field(default=True)


class DetailModel(BaseModel):
    detail: str
