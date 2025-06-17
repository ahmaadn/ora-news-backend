import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.db.models import load_all_models

# Load all models for testing
load_all_models()

# Create a test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create an async engine for testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

# Create an async session maker for testing
test_async_session_maker = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


def session_maker_factory():
    return test_async_session_maker


# Override the default session maker
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create the test database and tables."""
    # Delete test.db if it exists
    if os.path.exists("test.db"):  # noqa: PTH110
        os.unlink("test.db")  # noqa: PTH108

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Clean up - close connections and optionally drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

    # Delete test.db after tests
    if os.path.exists("test.db"):  # noqa: PTH110
        os.unlink("test.db")  # noqa: PTH108


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_async_session_maker() as session:
        yield session
        # Rollback at the end of each test
        await session.rollback()
