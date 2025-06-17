from unittest.mock import Mock

import pytest

from app.utils import exceptions
from app.utils.common import ErrorCode
from app.utils.validator import validate_username


def test_validate_username_valid():
    user = Mock()
    username = "valid_user"
    assert validate_username(username, user) == username


def test_validate_username_invalid_format():
    user = Mock()
    invalid_usernames = ["1invalid", "Invalid", "user@name", "user name"]
    for username in invalid_usernames:
        with pytest.raises(exceptions.ValidationError) as exc_info:
            validate_username(username, user)
        assert exc_info.value.error_code == ErrorCode.INVALID_USERNAME
        assert "Username must start with a letter" in str(exc_info.value)


def test_validate_username_too_short():
    user = Mock()
    username = "usr"
    with pytest.raises(exceptions.ValidationError) as exc_info:
        validate_username(username, user)
    assert exc_info.value.error_code == ErrorCode.INVALID_USERNAME
    assert "Username must be between 5 and 20 characters long" in str(exc_info.value)


def test_validate_username_too_long():
    user = Mock()
    username = "a" * 21
    with pytest.raises(exceptions.ValidationError) as exc_info:
        validate_username(username, user)
    assert exc_info.value.error_code == ErrorCode.INVALID_USERNAME
