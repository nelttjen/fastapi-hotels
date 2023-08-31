from typing import Optional, TypeVar

from fastapi import HTTPException, status

HTTP_EXC = TypeVar('HTTP_EXC', bound=HTTPException)


class BadRequest(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Bad request'
    headers = None

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=self.headers,
        )


class Unauthorized(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Unauthorized'
    headers = None

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=self.headers,
        )


class Forbidden(HTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Forbidden'
    headers = None

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=self.headers,
        )


class NotFound(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Requested resource not found'
    headers = None

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=self.headers,
        )


class DataConflict(HTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'Data conflicts with database instances'
    headers = None

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=self.headers,
        )
