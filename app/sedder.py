# HOW TO RUN, IN ROOT FOLDER RUN TERMINAL
# python3 -m app.seeder
# or
# py -m app.seeder


from app.db.factories.user_factory import UserFactory
from app.db.seed import Seeder


async def main(
    clear_all: bool = False,
    user_count: int = 10,
):
    """Main function to handle seeding logic."""
    seeder = Seeder()

    # Update factory sizes based on arguments
    seeder.factories = [
        {"factory": UserFactory, "size": user_count},
    ]

    # Factory for clear
    seeder.clear_factories = [
        UserFactory,  # include user and admin
    ]

    if clear_all:
        await seeder.clear_all()

    await seeder.seed()


if __name__ == "__main__":
    import fire

    fire.Fire(main)
