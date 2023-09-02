from pydantic import BaseModel, Field


class BaseORMModel(BaseModel):

    class Config:
        from_attributes = True


class SuccessModel(BaseModel):
    success: bool = Field(default=True)


class DetailModel(BaseModel):
    detail: str
