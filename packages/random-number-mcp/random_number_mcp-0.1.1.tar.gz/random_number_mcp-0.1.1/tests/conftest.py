"""Test configuration for random-number-mcp."""

from typing import Any

import pytest


@pytest.fixture
def sample_population() -> list[Any]:
    """Sample population for testing random choices."""
    return ["apple", "banana", "cherry", "date", "elderberry"]


@pytest.fixture
def sample_numbers() -> list[int]:
    """Sample numbers for testing shuffle operations."""
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@pytest.fixture
def sample_weights() -> list[float]:
    """Sample weights for testing weighted choices."""
    return [0.1, 0.2, 0.3, 0.25, 0.15]
