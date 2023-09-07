import datetime
import hashlib

from src.auth.models import VerificationCode, CodeTypes
from src.base.repositories import AbstractMongoRepository
from src.auth.config import EMAIL_CODE_EXPIRE_MINUTES


class VerificationCodeRepository(AbstractMongoRepository[VerificationCode]):

    class Meta:
        bind_model = VerificationCode

    async def check_code_exists(self, user_id: int, code_type: CodeTypes) -> VerificationCode | None:
        code = self.find_one(
            user_id=user_id,
            code_type=code_type.value,
        )

        if code and code.is_expired():
            self.delete(code)
            code = None

        return code

    async def generate_verification_code(self, user_id, code_type: CodeTypes) -> VerificationCode:
        code_hash = hashlib.sha256(str(user_id + datetime.datetime.utcnow().timestamp()).encode()).hexdigest()
        verification_code = VerificationCode(
            user_id=user_id,
            code=code_hash,
            code_type=code_type,
            expires=int(
                (datetime.datetime.utcnow() + datetime.timedelta(minutes=EMAIL_CODE_EXPIRE_MINUTES)).timestamp(),
            ),
        )
        self.save(verification_code)
        return verification_code
