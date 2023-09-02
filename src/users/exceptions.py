from typing import Optional

from fastapi import HTTPException, status


class UsernameOrEmailAlreadyExists(HTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'User with this username already exists'

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=None,
        )


class PasswordValidationError(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Password validation failed'

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=None,
        )


class EmailValidationError(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Incorrect email format'

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers=None,
        )


class UsernameValidationError(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Incorrect username format'

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=None,
        )