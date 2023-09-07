from fastapi import WebSocketException, status

from src.base.exceptions import NotFound, Unauthorized


class BadCredentialsException(Unauthorized):
    """Used if credentials are invalid or user not found."""

    detail = 'Invalid credentials provided'
    headers = {'WWW-Authenticate': 'Bearer'}


class BadTokenException(Unauthorized):
    """Used if token is invalid or expired."""

    detail = 'Token expired or incorrect'
    headers = {'WWW-Authenticate': 'Bearer'}


class UserForRecoveryNotFound(NotFound):
    detail = 'User with this email not found'


class UserNotActiveException(Unauthorized):
    detail = 'Please check your email to activate your account'


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
