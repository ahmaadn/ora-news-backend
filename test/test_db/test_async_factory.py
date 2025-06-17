from test.conftest import session_maker_factory

from sqlalchemy import select

from app.db.factories.user_factory import UserFactory
from app.db.models.user import User
from app.utils.security import PasswordHelper


class SimpleUserFactory(UserFactory):
    """A simplified user factory for testing the AsyncFactory class."""

    class Meta:
        async_session_maker_factory = session_maker_factory

    first_name = "Test"
    last_name = "User"
    is_active = True
    is_verified = False
    is_superuser = False


class SimpleAdminFactory(SimpleUserFactory):
    """A simplified admin factory for testing the AsyncFactory class."""

    first_name = "Admin"
    last_name = "User"
    is_active = True
    is_verified = True
    is_superuser = True


class TestAsyncFactory:
    async def test_create(self, db_session):
        # Ensure the database schema is initialized
        """Test that AsyncFactory.create() works correctly."""
        user = await SimpleUserFactory.create()

        assert user.first_name == "Test"
        assert user is not None
        assert isinstance(user, User)

        # Verify user was actually saved to database
        result = await db_session.execute(select(User).where(User.id == user.id))
        db_user = result.scalars().first()
        assert db_user is not None
        assert db_user.id == user.id

    async def test_create_batch(self, db_session):
        """Test that AsyncFactory.create_batch() works correctly."""
        batch_size = 3
        users = await SimpleUserFactory.create_batch(batch_size)

        assert len(users) == batch_size
        assert all(isinstance(user, User) for user in users)

        # Verify all users were saved to database
        for user in users:
            db_user = await db_session.get(User, user.id)
            assert db_user is not None

    async def test_async_factory_clear(self, db_session):
        """Test that AsyncFactory.clear() removes all instances."""
        # Create some users
        await SimpleUserFactory.create_batch(3)

        # Clear all users
        await SimpleUserFactory.clear()

        # Verify no users remain
        result = await db_session.execute(select(User))
        users = result.scalars().all()
        assert len(users) == 0

    async def test_custom_attributes(self, db_session):
        """Test creating objects with custom attribute values."""
        custom_username = "custom_user"
        custom_email = "custom@example.com"

        user = await SimpleUserFactory.create(
            username=custom_username, email=custom_email
        )

        assert user.username == custom_username
        assert user.email == custom_email

        # Verify custom values were saved to database
        async with db_session as session:
            db_user = await session.get(User, user.id)
            assert db_user.username == custom_username
            assert db_user.email == custom_email


class TestUserFactory:
    """Tests for UserFactory."""

    async def test_user_factory_create(self):
        """Test creating a user instance."""

        user = await SimpleUserFactory.create()

        # Check that the user was created with all required fields
        assert isinstance(user, User)
        assert (user.id) is not None
        assert user.username is not None
        assert user.email is not None
        assert user.hashed_password is not None
        assert user.name is not None

        # Check timestamps
        assert user.create_at is not None
        assert user.update_at is not None

        # Verify the password was hashed
        password_helper = PasswordHelper()
        print()
        assert password_helper.verify("123456789", user.hashed_password)

    async def test_user_factory_create_batch(self):
        """Test creating multiple users at once."""
        # Patch the async_session_maker to use our test session

        batch_size = 5
        users = await SimpleUserFactory.create_batch(batch_size)

        assert len(users) == batch_size
        for user in users:
            assert isinstance(user, User)
            assert user.id is not None

        # Check that each user has a unique ID and username
        ids = [user.id for user in users]
        usernames = [user.username for user in users]
        assert len(set(ids)) == batch_size
        assert len(set(usernames)) == batch_size

    async def test_user_factory_with_custom_fields(self):
        """Test creating a user with custom field values."""

        custom_username = "testuser123"
        custom_email = "test@example.com"

        user = await SimpleUserFactory.create(
            username=custom_username,
            email=custom_email,
            is_active=True,
            is_verified=True,
        )

        assert user.username == custom_username
        assert user.email == custom_email
        assert user.is_active is True
        assert user.is_verified is True
        assert user.is_superuser is False  # Default value

    async def test_admin_user_factory(self):
        """Test creating an admin user."""

        admin = await SimpleAdminFactory.create()

        assert isinstance(admin, User)
        assert admin.name == "Admin"
        assert admin.is_active is True
        assert admin.is_verified is True
