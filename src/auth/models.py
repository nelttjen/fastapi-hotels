import datetime
from enum import Enum

from src.base.models import MongoModel


class CodeTypes(str, Enum):
    RECOVERY = 'recovery'
    ACTIVATION = 'activation'


class VerificationCode(MongoModel):
    user_id: int
    code: str
    code_type: CodeTypes
    expires: int

    class Meta:
        __collection__ = 'verification_codes'

    def is_expired(self) -> bool:
        return int(datetime.datetime.utcnow().timestamp()) > self.expires
