import factory
from faker import Faker

from app.db.factories.base import AsyncFactory
from app.db.factories.category_factory import CategoryFactory
from app.db.factories.user_factory import UserFactory
from app.db.models.news import News

fake = Faker()


class NewsFactory(AsyncFactory):
    class Meta:
        model = News

    title = factory.LazyAttribute(lambda x: fake.sentence())
    content = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=300))
    image_url = factory.LazyAttribute(lambda x: fake.image_url())
    published_at = factory.LazyAttribute(lambda x: fake.date_time_this_year())

    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")

    category = factory.SubFactory(CategoryFactory)
    category_id = factory.SelfAttribute("category.id")
