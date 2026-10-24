import pytest
from app.config.settings import get_settings
from app.fallback.circuit_breaker import circuit_breaker
from app.storage.database import engine


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    """
    Session-level fixture to set fast provider timeouts and zero retries during tests.
    """
    settings = get_settings()
    original_timeout = settings.PROVIDER_TIMEOUT_SECONDS
    original_retries = settings.MAX_RETRIES

    settings.PROVIDER_TIMEOUT_SECONDS = 0.2
    settings.MAX_RETRIES = 0

    yield

    settings.PROVIDER_TIMEOUT_SECONDS = original_timeout
    settings.MAX_RETRIES = original_retries


@pytest.fixture(autouse=True)
def reset_circuit_breakers():
    """Reset circuit breakers before each test to maintain test isolation."""
    circuit_breaker.failures.clear()
    circuit_breaker.last_failure_time.clear()
    circuit_breaker.half_open_pending.clear()
    yield


@pytest.fixture(autouse=True)
async def dispose_database_connections():
    """
    Ensure all async database connections in the pool are closed before
    the test's event loop closes, preventing aiosqlite 'Event loop is closed' thread errors.
    """
    yield
    await engine.dispose()
