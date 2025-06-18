import re

from email_validator import EmailNotValidError
from email_validator import validate_email as validate_email_
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.utils import exceptions
from app.utils.common import ErrorCode

USERNAME_REGEX = re.compile(r"^[a-z][a-z0-9_-]{2,19}$")


def validate_username(username: str, user):
    if not USERNAME_REGEX.match(username):
        raise exceptions.ValidationError(
            "Username must start with a letter",
            "can only contain lowercase letters, numbers, underscores, or hyphens.",
            error_code=ErrorCode.INVALID_USERNAME,
        )
    if len(username) < 5 or len(username) > 20:
        raise exceptions.ValidationError(
            "Username must be between 5 and 20 characters long",
            error_code=ErrorCode.INVALID_USERNAME,
        )
    return username


def validate_email(email: str, user):
    try:
        validate_email_(email, test_environment=get_settings().DEBUG_MODE)
    except EmailNotValidError as e:
        raise exceptions.ValidationError(
            "Invalid email address", error_code=ErrorCode.INVALID_EMAIL
        ) from e
    return email


def validate_password(password: str, user):
    if len(password) < 8:
        raise exceptions.ValidationError(
            "Password must be at least 8 characters long",
            error_code=ErrorCode.INVALID_PASSOWRD,
        )
    if user.email in password:
        raise exceptions.ValidationError(
            "Password should not contain email",
            error_code=ErrorCode.INVALID_PASSOWRD,
        )
    if user.username in password:
        raise exceptions.ValidationError(
            "Password should not contain username",
            error_code=ErrorCode.INVALID_PASSOWRD,
        )
    return password


def validate_file_image(file: UploadFile):
    allowed_extensions = {"image/jpeg", "image/png"}
    if file.content_type not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=exceptions.FormatFileNotAllowedError(
                "Invalid file type. Only JPG and PNG are allowed.",
                error_code=ErrorCode.FORMAT_IMAGE_NOT_ALLOWED,
            ).dump(),
        )
