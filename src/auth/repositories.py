import datetime
import hashlib

from src.auth.config import auth_config
from src.auth.models import CodeTypes, EmailCodeSent, VerificationCode
from src.base.repositories import AbstractMongoRepository
from src.base.utils import get_utcnow


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
        code_hash = hashlib.sha256(str(user_id + get_utcnow().timestamp()).encode()).hexdigest()
        verification_code = VerificationCode(
            user_id=user_id,
            code=code_hash,
            code_type=code_type,
            expires=int(
                (get_utcnow() + datetime.timedelta(
                    seconds=auth_config.EMAIL_CODE_EXPIRE_MINUTES,
                )).timestamp(),
            ),
        )
        self.save(verification_code)
        return verification_code

    async def get_valid_code(self, code: str) -> VerificationCode | None:
        code = self.find_one(
            code=code,
        )

        if code and code.is_expired():
            self.delete(code)
            code = None
        return code


class EmailCodeSentRepository(AbstractMongoRepository[EmailCodeSent]):

    class Meta:
        bind_model = EmailCodeSent

    async def get_email_rate_limit_model(self, email: str, code_type: CodeTypes) -> EmailCodeSent:
        instance = self.find_one(
            email=email,
            code_type=code_type.value,
        )

        if not instance:
            instance = EmailCodeSent(
                email=email,
                code_type=code_type,
                last_sent=0,
            )

            self.save(instance)

        return instance

    async def update_last_sent(self, instance: EmailCodeSent) -> None:
        instance.last_sent = int(get_utcnow().timestamp())
        self.save(instance)
