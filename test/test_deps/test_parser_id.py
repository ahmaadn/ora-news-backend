import uuid

import pytest

from app.api.dependencies.user_manager import UserManager
from app.utils import exceptions
from app.utils.common import ErrorCode


@pytest.fixture
def user_manager():
    """Fixture to create a UserManager instance with a mock session."""

    class MockSession:
        pass

    return UserManager(session=MockSession())


def test_parse_id_valid_uuid(user_manager):
    """Test parse_id with a valid UUID."""
    valid_uuid = uuid.uuid4()
    result = user_manager.parse_id(valid_uuid)
    assert result == valid_uuid


def test_parse_id_valid_uuid_string(user_manager):
    """Test parse_id with a valid UUID string."""
    valid_uuid = uuid.uuid4()
    result = user_manager.parse_id(str(valid_uuid))
    assert result == valid_uuid


def test_parse_id_invalid_uuid_string(user_manager):
    """Test parse_id with an invalid UUID string."""
    invalid_uuid = "invalid-uuid-string"
    with pytest.raises(exceptions.InvalidIDError) as exc_info:
        user_manager.parse_id(invalid_uuid)
    assert exc_info.value.error_code == ErrorCode.INVALID_USER_UUID


def test_parse_id_non_uuid_type(user_manager):
    """Test parse_id with a non-UUID type."""
    non_uuid_value = 12345
    with pytest.raises(exceptions.InvalidIDError) as exc_info:
        user_manager.parse_id(non_uuid_value)
    assert exc_info.value.error_code == ErrorCode.INVALID_USER_UUID
