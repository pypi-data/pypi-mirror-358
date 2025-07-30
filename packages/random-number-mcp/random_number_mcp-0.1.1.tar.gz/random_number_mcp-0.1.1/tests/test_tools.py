"""Tests for the random number tools."""

import re
from typing import Any

import pytest

from random_number_mcp.server import (
    random_choices as server_random_choices,
)
from random_number_mcp.tools import (
    random_choices,
    random_float,
    random_int,
    random_sample,
    random_shuffle,
    secure_random_int,
    secure_token_hex,
)


class TestRandomInt:
    """Tests for random_int function."""

    def test_random_int_basic(self):
        """Test basic random integer generation."""
        result = random_int(1, 10)
        assert isinstance(result, int)
        assert 1 <= result <= 10

    def test_random_int_same_bounds(self):
        """Test random integer with same low and high."""
        result = random_int(5, 5)
        assert result == 5

    def test_random_int_negative_range(self):
        """Test random integer with negative range."""
        result = random_int(-10, -1)
        assert isinstance(result, int)
        assert -10 <= result <= -1

    def test_random_int_invalid_range(self):
        """Test random integer with invalid range."""
        with pytest.raises(ValueError, match="Low value .* must be <= high value"):
            random_int(10, 5)

    def test_random_int_non_integer_input(self):
        """Test random integer with non-integer input."""
        with pytest.raises(TypeError, match="Both low and high must be integers"):
            random_int(1.5, 10)

        with pytest.raises(TypeError, match="Both low and high must be integers"):
            random_int(1, "10")


class TestRandomFloat:
    """Tests for random_float function."""

    def test_random_float_basic(self):
        """Test basic random float generation."""
        result = random_float(0.0, 1.0)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_random_float_default_args(self):
        """Test random float with default arguments."""
        result = random_float()
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_random_float_custom_range(self):
        """Test random float with custom range."""
        result = random_float(10.5, 20.7)
        assert isinstance(result, float)
        assert 10.5 <= result <= 20.7

    def test_random_float_invalid_range(self):
        """Test random float with invalid range."""
        with pytest.raises(ValueError, match="Low value .* must be <= high value"):
            random_float(5.0, 2.0)

    def test_random_float_non_numeric_input(self):
        """Test random float with non-numeric input."""
        with pytest.raises(TypeError, match="Both low and high must be numeric"):
            random_float("1.0", 5.0)


class TestRandomChoices:
    """Tests for random_choices function."""

    def test_random_choices_basic(self, sample_population: list[Any]):
        """Test basic random choices."""
        result = random_choices(sample_population)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] in sample_population

    def test_random_choices_multiple(self, sample_population: list[Any]):
        """Test random choices with multiple selections."""
        result = random_choices(sample_population, k=3)
        assert isinstance(result, list)
        assert len(result) == 3
        for item in result:
            assert item in sample_population

    def test_random_choices_with_weights(
        self, sample_population: list[Any], sample_weights: list[float]
    ):
        """Test random choices with weights."""
        result = random_choices(sample_population, k=2, weights=sample_weights)
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert item in sample_population

    def test_random_choices_empty_population(self):
        """Test random choices with empty population."""
        with pytest.raises(ValueError, match="population cannot be empty"):
            random_choices([])

    def test_random_choices_negative_k(self, sample_population: list[Any]):
        """Test random choices with negative k."""
        with pytest.raises(ValueError, match="k must be non-negative"):
            random_choices(sample_population, k=-1)

    def test_random_choices_non_integer_k(self, sample_population: list[Any]):
        """Test random choices with non-integer k."""
        with pytest.raises(TypeError, match="k must be an integer"):
            random_choices(sample_population, k=1.5)

    def test_random_choices_mismatched_weights(self, sample_population: list[Any]):
        """Test random choices with mismatched weights length."""
        with pytest.raises(
            ValueError, match="Weights list length .* must match population length"
        ):
            random_choices(sample_population, weights=[0.5, 0.5])

    def test_random_choices_with_string_weights(self, sample_population: list[Any]):
        """Test random choices with weights as a JSON string."""
        weights_str = "[1, 3, 5, 2, 2]"
        # Note: We are testing the server-level function here
        result = server_random_choices.fn(
            population=sample_population, k=3, weights=weights_str
        )
        assert isinstance(result, list)
        assert len(result) == 3
        for item in result:
            assert item in sample_population

    def test_random_choices_with_invalid_json_string_weights(
        self, sample_population: list[Any]
    ):
        """Test random choices with an invalid JSON string for weights."""
        weights_str = "[0.1, 0.2, 0.3, 0.25, 0.15"  # Invalid JSON
        with pytest.raises(ValueError, match="Invalid JSON string for weights"):
            server_random_choices.fn(
                population=sample_population, k=1, weights=weights_str
            )

    def test_random_choices_with_mismatched_string_weights(
        self, sample_population: list[Any]
    ):
        """Test random choices with mismatched weights length in a string."""
        weights_str = "[0.5, 0.5]"
        with pytest.raises(
            ValueError, match="Weights list length .* must match population length"
        ):
            server_random_choices.fn(
                population=sample_population, k=1, weights=weights_str
            )


class TestRandomShuffle:
    """Tests for random_shuffle function."""

    def test_random_shuffle_basic(self, sample_numbers: list[int]):
        """Test basic random shuffle."""
        result = random_shuffle(sample_numbers)
        assert isinstance(result, list)
        assert len(result) == len(sample_numbers)
        assert set(result) == set(sample_numbers)
        assert result is not sample_numbers  # Ensure it's a new list

    def test_random_shuffle_single_item(self):
        """Test random shuffle with single item."""
        items = ["single"]
        result = random_shuffle(items)
        assert result == ["single"]
        assert result is not items

    def test_random_shuffle_empty_list(self):
        """Test random shuffle with empty list."""
        with pytest.raises(ValueError, match="items cannot be empty"):
            random_shuffle([])

    def test_random_shuffle_preserves_original(self, sample_numbers: list[int]):
        """Test that random shuffle preserves the original list."""
        original = sample_numbers.copy()
        random_shuffle(sample_numbers)
        assert sample_numbers == original  # Original unchanged


class TestRandomSample:
    """Tests for random_sample function."""

    def test_random_sample_basic(self, sample_population: list[Any]):
        """Test basic random sample."""
        result = random_sample(sample_population, k=1)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] in sample_population

    def test_random_sample_multiple(self, sample_population: list[Any]):
        """Test random sample with multiple selections."""
        result = random_sample(sample_population, k=3)
        assert isinstance(result, list)
        assert len(result) == 3
        for item in result:
            assert item in sample_population
        assert len(set(result)) == 3  # Ensure no replacement

    def test_random_sample_all_items(self, sample_population: list[Any]):
        """Test random sample with k equal to population size."""
        result = random_sample(sample_population, k=len(sample_population))
        assert isinstance(result, list)
        assert len(result) == len(sample_population)
        assert set(result) == set(sample_population)

    def test_random_sample_empty_population(self):
        """Test random sample with empty population."""
        with pytest.raises(ValueError, match="population cannot be empty"):
            random_sample([], k=0)

    def test_random_sample_negative_k(self, sample_population: list[Any]):
        """Test random sample with negative k."""
        with pytest.raises(ValueError, match="k must be non-negative"):
            random_sample(sample_population, k=-1)

    def test_random_sample_k_greater_than_population(
        self, sample_population: list[Any]
    ):
        """Test random sample with k greater than population size."""
        with pytest.raises(
            ValueError, match="Sample size k cannot be greater than population size"
        ):
            random_sample(sample_population, k=len(sample_population) + 1)

    def test_random_sample_non_integer_k(self, sample_population: list[Any]):
        """Test random sample with non-integer k."""
        with pytest.raises(TypeError, match="k must be an integer"):
            random_sample(sample_population, k=1.5)


class TestSecureTokenHex:
    """Tests for secure_token_hex function."""

    def test_secure_token_hex_default(self):
        """Test secure token hex with default bytes."""
        result = secure_token_hex()
        assert isinstance(result, str)
        assert len(result) == 64  # 32 bytes * 2 hex chars per byte
        assert re.match(r"^[0-9a-f]+$", result)

    def test_secure_token_hex_custom_bytes(self):
        """Test secure token hex with custom byte count."""
        result = secure_token_hex(16)
        assert isinstance(result, str)
        assert len(result) == 32  # 16 bytes * 2 hex chars per byte
        assert re.match(r"^[0-9a-f]+$", result)

    def test_secure_token_hex_zero_bytes(self):
        """Test secure token hex with zero bytes."""
        result = secure_token_hex(0)
        assert result == ""

    def test_secure_token_hex_negative_bytes(self):
        """Test secure token hex with negative bytes."""
        with pytest.raises(ValueError, match="nbytes must be non-negative"):
            secure_token_hex(-1)

    def test_secure_token_hex_non_integer(self):
        """Test secure token hex with non-integer input."""
        with pytest.raises(TypeError, match="nbytes must be an integer"):
            secure_token_hex(1.5)


class TestSecureRandomInt:
    """Tests for secure_random_int function."""

    def test_secure_random_int_basic(self):
        """Test basic secure random integer."""
        result = secure_random_int(100)
        assert isinstance(result, int)
        assert 0 <= result < 100

    def test_secure_random_int_small_bound(self):
        """Test secure random integer with small bound."""
        result = secure_random_int(1)
        assert result == 0

    def test_secure_random_int_zero_bound(self):
        """Test secure random integer with zero bound."""
        with pytest.raises(ValueError, match="upper_bound must be positive"):
            secure_random_int(0)

    def test_secure_random_int_negative_bound(self):
        """Test secure random integer with negative bound."""
        with pytest.raises(ValueError, match="upper_bound must be positive"):
            secure_random_int(-5)

    def test_secure_random_int_non_integer(self):
        """Test secure random integer with non-integer input."""
        with pytest.raises(TypeError, match="upper_bound must be an integer"):
            secure_random_int(10.5)
