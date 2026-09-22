"""
Root pytest fixtures shared by tests/, hive/tests/, and other test roots.

hive/tests/ does not inherit tests/conftest.py; without this file those suites
run without ENVIRONMENT=test and fail StateManager's production secret check.
"""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars() -> Generator[None, None, None]:
    """Set test environment variables for all collected tests."""
    test_env = {
        "GOOGLE_API_KEY": "test_google_api_key",
        "LOG_LEVEL": "DEBUG",
        "ENVIRONMENT": "test",
        "HIVE_SECRET_KEY": "test_secret_key_for_ci",
        "STORAGE_TYPE": "FILE",
    }
    with patch.dict(os.environ, test_env):
        yield
