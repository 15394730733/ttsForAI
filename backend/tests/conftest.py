"""
Pytest configuration and fixtures.

Provides shared fixtures for all tests.
"""
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from tests.utils import clear_test_database, clear_test_queue


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session.

    Yields:
        AsyncSession: Test database session
    """
    # Create in-memory database for testing
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    # Clean up
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession):
    """
    Create test HTTP client.

    Args:
        test_db: Test database session

    Yields:
        AsyncClient: Test HTTP client
    """
    from src.main import app

    # Override get_db dependency to use test database
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Use raise_app_exceptions=False to handle lifespan issues
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_data_dir() -> Path:
    """
    Get test data directory.

    Returns:
        Path: Test data directory path
    """
    return Path(__file__).parent / "data"


@pytest.fixture(scope="function", autouse=True)
async def cleanup_test_state(test_db: AsyncSession):
    """
    Automatically clean up test state after each test.

    This fixture runs automatically after every test to ensure
    test isolation by clearing the database and queue.

    Args:
        test_db: Test database session
    """
    # Run the test
    yield

    # Clean up after test
    try:
        # Clear database first
        await clear_test_database(test_db)

        # Clear queue synchronously (queue is global state)
        try:
            await queue_service.clear_queue()
        except:
            # If queue clear fails, try to at least drain it
            queue_size = queue_service.get_queue_size()
            for _ in range(queue_size):
                if not queue_service.is_empty():
                    try:
                        await queue_service.dequeue()
                    except:
                        break

    except Exception as e:
        # Log but don't fail the test if cleanup fails
        print(f"Warning: Cleanup failed: {e}")
