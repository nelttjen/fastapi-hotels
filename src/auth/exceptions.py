from fastapi import WebSocketException, status

from src.base.exceptions import (BadRequest, NotFound, TooManyRequests,
                                 Unauthorized)


class BadCredentialsException(Unauthorized):
    """Used if credentials are invalid or user not found."""

    detail = 'Invalid credentials provided'
    headers = {'WWW-Authenticate': 'Bearer'}


class BadTokenException(Unauthorized):
    """Used if token is invalid or expired."""

    detail = 'Token expired or incorrect'
    headers = {'WWW-Authenticate': 'Bearer'}


class UserForEmailCodeNotFound(NotFound):
    """Used if user with this email not found when creating request to send
    email code."""

    detail = 'User with this email not found'


class UserNotActiveException(Unauthorized):
    """Used if user is not active and trying to authenticate."""

    detail = 'Please check your email to activate your account'


class InvalidEmailCode(BadRequest):
    """Used if email code is invalid or expired."""

    detail = 'Code you provided is expired or incorrect'


class EmailRateLimit(TooManyRequests):
    """User already got an email with this type of code."""

    detail = 'Email rate limit exceeded. Please try again later'


class WebSocketBadTokenException(WebSocketException):
    """WebSocket exception for bad token.

    Used of token is invalid or expired.
    """

    detail = 'WebSocket Token expired or incorrect'
    status_code = status.WS_1008_POLICY_VIOLATION

    def __init__(self):
        super().__init__(
            code=self.status_code,
        )
