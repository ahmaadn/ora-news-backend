# HOW TO RUN, IN ROOT FOLDER RUN TERMINAL
# python3 -m app.seeder
# or
# py -m app.seeder


from app.db.factories.category_factory import CategoryFactory
from app.db.factories.news_factory import NewsFactory
from app.db.factories.user_factory import UserFactory
from app.db.seed import Seeder


async def main(
    clear_all: bool = False,
    user_count: int = 10,
    category_count: int = 10,
    news_count: int = 10,
):
    """Main function to handle seeding logic."""
    seeder = Seeder()

    # Update factory sizes based on arguments
    seeder.factories = [
        {"factory": CategoryFactory, "size": category_count},
        {
            "factory": NewsFactory,
            "size": news_count,
            "user_id": "cce0f12f-3ad4-40b2-b911-b66ee27fc095",
        },
    ]

    # Factory for clear
    seeder.clear_factories = [
        NewsFactory,
        CategoryFactory,  # include user and admin
        UserFactory,
    ]

    if clear_all:
        await seeder.clear_all()

    await seeder.seed()


if __name__ == "__main__":
    import fire

    fire.Fire(main)
