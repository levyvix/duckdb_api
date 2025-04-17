import os
from collections.abc import Generator

import pandas as pd
import pytest
from _pytest.fixtures import FixtureRequest


@pytest.fixture
def sample_data() -> list[dict]:
    """Return sample data for testing."""
    return [
        {"id": 1, "title": "Test Post 1", "body": "Content 1"},
        {"id": 2, "title": "Test Post 2", "body": "Content 2"},
    ]


@pytest.fixture
def sample_df(sample_data) -> pd.DataFrame:
    """Return a sample DataFrame for testing."""
    return pd.DataFrame(sample_data)


@pytest.fixture
def temp_db_path(request: FixtureRequest) -> Generator[str, None, None]:
    """Create a temporary database path and clean up after tests."""
    db_path = "test_data.duckdb"
    yield db_path
    # Cleanup after test
    if os.path.exists(db_path):
        os.remove(db_path)
