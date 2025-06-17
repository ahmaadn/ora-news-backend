from typing import Any, ClassVar

import jwt
from pydantic import SecretStr

from app.core.config import get_settings
from app.db.models.user import User
from app.utils import exceptions
from app.utils.common import ErrorCode
from app.utils.jwt import create_jwt_token, decode_jwt_token


class TokenManager:
    JWT_AUDIENCE: ClassVar[str] = "users:auth"
    JWT_SECRET_KEY: ClassVar[str] = get_settings().JWT_SECRET_KEY
    JWT_LIFETIME_SECONDS: ClassVar[int] = get_settings().JWT_LIFETIME_SECONDS

    REFRESH_AUDIENCE: ClassVar[str] = "users:refresh"
    REFRESH_SECRET_KEY: ClassVar[str] = get_settings().JWT_SECRET_KEY
    REFRESH_LIFETIME_SECONDS: ClassVar[str] = get_settings().JWT_LIFETIME_SECONDS * 2

    VERIFICATION_AUDIENCE: ClassVar[str] = "users:verify"
    VERIFICATION_SECRET_KEY: ClassVar[str] = get_settings().VERIFICATION_SECRET_KEY
    VERIFICATION_LIFETIME_SECONDS: ClassVar[int] = get_settings().VERIFICATION_LIFETIME_SECONDS

    RESET_PASSWORD_AUDIENCE: ClassVar[str] = "users:forget-password"
    RESET_PASSWORD_SECRET_KEY: ClassVar[str] = get_settings().RESET_PASSWORD_SECRET_KEY
    RESET_PASSWORD_LIFETIME_SECONDS: ClassVar[int] = (
        get_settings().RESET_PASSWORD_LIFETIME_SECONDS
    )

    def _write_token(
        self,
        sub: Any,
        aud: str,
        secret: str,
        lifetime: int,
        other_payload: dict | None = None,
    ):
        if other_payload is None:
            other_payload = {}
        playload = {"sub": sub, "aud": aud, **other_payload}
        return create_jwt_token(playload, secret, lifetime)

    def create_access_token(self, user: User) -> str:
        """Create an access token for the user."""
        return self._write_token(
            sub=str(user.id),
            aud=self.JWT_AUDIENCE,
            secret=self.JWT_SECRET_KEY,
            lifetime=self.JWT_LIFETIME_SECONDS,
        )

    def create_refresh_token(self, access_token: str) -> str:
        """Create a refresh token for the user."""
        return self._write_token(
            sub=access_token,
            aud=self.REFRESH_AUDIENCE,
            secret=self.REFRESH_SECRET_KEY,
            lifetime=self.REFRESH_LIFETIME_SECONDS,
        )

    def create_forget_password_token(self, user: User) -> str:
        """Create a token for resetting the user's password."""
        if not user.is_active:
            raise exceptions.UserInactiveError(
                "User is inactive", error_code=ErrorCode.USER_NOT_ACTIVE
            )

        return self._write_token(
            sub=str(user.id),
            aud=self.RESET_PASSWORD_AUDIENCE,
            secret=self.RESET_PASSWORD_SECRET_KEY,
            lifetime=self.RESET_PASSWORD_LIFETIME_SECONDS,
        )

    def create_verification_token(self, user: User) -> str:
        """Create a token for verifying the user's email."""
        if not user.is_active:
            raise exceptions.UserInactiveError(
                "User is inactive", error_code=ErrorCode.USER_NOT_ACTIVE
            )
        if user.is_verified:
            raise exceptions.UserAlreadyVerifiedError(
                "User already verified", error_code=ErrorCode.USER_ALREADY_VERIFIED
            )

        return self._write_token(
            sub=str(user.id),
            aud=self.VERIFICATION_AUDIENCE,
            secret=self.VERIFICATION_SECRET_KEY,
            lifetime=self.VERIFICATION_LIFETIME_SECONDS,
            other_payload={"email": user.email},
        )

    def decode_token(
        self,
        token: str,
        secret: str | SecretStr,
        audience: list[str],
    ):
        try:
            return decode_jwt_token(token, secret, audience)
        except jwt.PyJWTError as e:
            raise exceptions.InvalidVerifyTokenError(
                "Invalid verify token", error_code=ErrorCode.INVALID_TOKEN
            ) from e
