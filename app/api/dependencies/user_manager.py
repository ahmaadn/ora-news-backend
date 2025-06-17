import uuid
from typing import Any

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.sessions import get_async_session
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils import exceptions
from app.utils.common import ErrorCode
from app.utils.security import PasswordHelper
from app.utils.validator import validate_email, validate_password, validate_username


class UserManager:
    def __init__(
        self,
        session: AsyncSession,
        password_helper: PasswordHelper | None = None,
    ):
        self.session: AsyncSession = session
        self.password_helper = (
            PasswordHelper() if password_helper is None else password_helper
        )

    def parse_id(self, value: Any) -> uuid.UUID:
        """Parse a value to a UUID.

        Args:
            value (Any): value to parse

        Raises:
            exceptions.InvalidIDError: if the value is not a valid UUID

        Returns:
            uuid.UUID: parsed UUID
        """
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except (ValueError, AttributeError) as e:
            raise exceptions.InvalidIDError(
                "Invalid UUID", error_code=ErrorCode.INVALID_USER_UUID
            ) from e

    async def _get_user(self, statement) -> User | None:
        """Get a user by statement."""
        result = await self.session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, _id: uuid.UUID) -> User | None:
        """Get a user by ID.

        Args:
            _id (uuid.UUID): id of the user

        Returns:
            User | None: user object or None if not found
        """
        statement = select(User).where(User.id == _id)
        return await self._get_user(statement)

    async def get_by_email(self, user_email: str) -> User:
        """Get a user by email.

        Args:
            user_email (str): email of the user

        Raises:
            exceptions.UserNotExistsError: if the user does not exist

        Returns:
            User: user object
        """
        statement = select(User).where(User.email == user_email)
        user = await self._get_user(statement)
        if not user:
            raise exceptions.UserNotExistsError(
                "User not found", error_code=ErrorCode.USER_NOT_EXISTS
            )
        return user

    async def get_by_username(self, username: str) -> User:
        """Get a user by username.

        Args:
            username (str): username of the user

        Raises:
            exceptions.UserNotExistsError: if the user does not exist

        Returns:
            User: user object
        """
        statement = select(User).where(User.username == username)
        user = await self._get_user(statement)
        if not user:
            raise exceptions.UserNotExistsError(
                "User not found", error_code=ErrorCode.USER_NOT_EXISTS
            )
        return user

    async def create(self, user_create: UserCreate, safe: bool = True) -> User:
        """Create a new user.

        Args:
            user_create (UserCreate): user_create model

        Raises:
            exceptions.UserAlreadyExistsError: if the user already exists
            exceptions.UserAlreadyExistsError: if the username already exists

        Returns:
            User: created user object
        """
        validate_email(user_create.email, user_create)
        validate_username(user_create.username, user_create)
        validate_password(user_create.password, user_create)

        try:
            existing_user = await self.get_by_email(user_create.email)
            if existing_user is not None:
                raise exceptions.UserAlreadyExistsError(
                    "user email already used",
                    error_code=ErrorCode.USER_EMAIL_ALREADY_USED,
                )
        except exceptions.UserNotExistsError:
            pass

        try:
            existing_user = await self.get_by_username(user_create.username)
            if existing_user is not None:
                raise exceptions.UserAlreadyExistsError(
                    "username already used",
                    error_code=ErrorCode.USERNAME_ALREADY_USED,
                )
        except exceptions.UserNotExistsError:
            pass

        # dump the user_create model to a dict
        if safe:
            user_dict = user_create.create_safe_dump_model()
        else:
            user_dict = user_create.create_dump_model_superuser()

        # hash the password
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        # create the user
        create_user = User(**user_dict)
        self.session.add(create_user)
        await self.session.commit()
        await self.session.refresh(create_user)

        return create_user

    async def update(
        self,
        user_update: UserUpdate,
        user: User,
        safe: bool = True,
        request: Request | None = None,
    ):
        if safe:
            updated_user_data = user_update.create_safe_dump_model()
        else:
            updated_user_data = user_update.create_dump_model_superuser()

        validate_user_data = await self._validate_update(user, updated_user_data)
        return await self._update_user(user, validate_user_data)

    async def delete(self, user: User, request: Request | None = None) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _validate_update(
        self, user: User, update_dict: dict[str, Any]
    ) -> dict[str, Any]:
        validated_update_dict = {}
        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                validate_email(value, user)
                try:
                    await self.get_by_email(user_email=value)
                    raise exceptions.UserAlreadyExistsError(
                        "User email already exists",
                        error_code=ErrorCode.USER_EMAIL_ALREADY_USED,
                    )
                except exceptions.UserNotExistsError:
                    validated_update_dict["email"] = value
                    validated_update_dict["is_verified"] = False
            elif field == "username" and value != user.username:
                validate_username(value, user)
                try:
                    await self.get_by_username(value)
                    raise exceptions.UserAlreadyExistsError(
                        "Username already exists",
                        error_code=ErrorCode.USERNAME_ALREADY_USED,
                    )
                except exceptions.UserNotExistsError:
                    validated_update_dict["username"] = value
            elif field == "password" and value is not None:
                validate_password(value, user)
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )
            else:
                validated_update_dict[field] = value
        return validated_update_dict

    async def _update_user(self, user: User, update_dict: dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(user, key, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def authenticate(self, credentials: OAuth2PasswordRequestForm):
        try:
            if credentials.username.isalnum():
                user = await self.get_by_username(credentials.username)
            else:
                user = await self.get_by_email(credentials.username)
        except exceptions.UserNotExistsError:
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self._update_user(user, {"hashed_password": updated_password_hash})

        return user


async def get_user_manager(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Dependency to get the user manager.
    """
    yield UserManager(session=session)
