import factory
from faker import Faker

from app.db.factories.base import AsyncFactory
from app.db.models.category import Category

fake = Faker()


class CategoryFactory(AsyncFactory):
    class Meta:
        model = Category

    name = factory.LazyFunction(lambda: fake.unique.user_name())
