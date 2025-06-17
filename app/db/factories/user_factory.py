from uuid import uuid4

import factory
from faker import Faker

from app.db.factories.base import AsyncFactory
from app.db.models.user import User
from app.utils.security import PasswordHelper

fake = Faker()


class UserFactory(AsyncFactory):
    """Factory for creating User model instances."""

    class Meta:
        model = User

    id = factory.LazyFunction(lambda: str(uuid4()))
    username = factory.LazyFunction(lambda: fake.unique.user_name())
    email = factory.LazyFunction(lambda: fake.unique.email())
    hashed_password = factory.LazyFunction(lambda: PasswordHelper().hash("123456789"))
    name = factory.LazyFunction(lambda: f"{fake.first_name()} {fake.last_name()}")

    is_active = factory.LazyFunction(lambda: fake.boolean())
    is_verified = factory.LazyFunction(lambda: fake.boolean())
