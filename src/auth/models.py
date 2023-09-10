import datetime
from enum import Enum

from pydantic import EmailStr

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


class EmailCodeSent(MongoModel):
    email: EmailStr
    code_type: CodeTypes
    last_sent: int

    class Meta:
        __collection__ = 'email_code_sent'

    def can_send_new_code(self, rate_limit: int) -> bool:
        last_sent = datetime.datetime.fromtimestamp(self.last_sent)
        return last_sent + datetime.timedelta(seconds=rate_limit) < datetime.datetime.utcnow()
