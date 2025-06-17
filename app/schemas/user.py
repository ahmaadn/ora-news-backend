from datetime import datetime
from typing import Any

from app.schemas.base import BaseSchema
from app.schemas.mixin import TimeStampMixinSchema, UUIDMixinSchema


class _BaseUserSchema(BaseSchema):
    def create_safe_dump_model(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True, exclude={"is_active", "is_verified"})

    def create_dump_model_superuser(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class UserRead(_BaseUserSchema, UUIDMixinSchema, TimeStampMixinSchema):
    username: str
    email: str
    name: str
    avatar_url: str | None = None
    is_active: bool = True
    is_verified: bool = False


class UserCreate(_BaseUserSchema):
    email: str
    username: str
    name: str
    password: str


class UserUpdate(_BaseUserSchema):
    email: str | None = None
    username: str | None = None
    name: str | None = None
    password: str | None = None


class VerifyUserUpdate(UserUpdate):
    is_verified: bool = False


class UserResetPasswordUpdate(UserUpdate):
    pending_password_hash: str | None = None
    password_change_token: str | None = None
    password_change_token_expires_at: datetime | None = None


class UserPasswordUpdate(UserUpdate):
    hashed_password: str
    pending_password_hash: str | None = None
    password_change_token: str | None = None
    password_change_token_expires_at: datetime | None = None
