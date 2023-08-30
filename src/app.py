import dataclasses
from typing import Literal

import pydantic.main
from fastapi import FastAPI, Depends
from pydantic import ValidationError, BaseModel, field_validator, validator
from datetime import datetime

app = FastAPI()


@app.get('/test')
async def test(
        value: Literal['val1', 'val2', 'val3'],
):
    return {'value': value}
