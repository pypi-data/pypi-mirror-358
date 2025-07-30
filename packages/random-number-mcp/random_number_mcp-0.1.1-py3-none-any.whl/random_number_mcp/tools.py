"""Random number tools for the MCP server."""

import random
import secrets
from typing import Any

from .utils import (
    validate_list_not_empty,
    validate_positive_int,
    validate_range,
    validate_weights_match_population,
)


def random_int(low: int, high: int) -> int:
    """Generate a random integer between low and high (inclusive).

    Args:
        low: Lower bound (inclusive)
        high: Upper bound (inclusive)

    Returns:
        Random integer between low and high

    Raises:
        ValueError: If low > high
        TypeError: If inputs are not integers
    """
    if not isinstance(low, int) or not isinstance(high, int):
        raise TypeError("Both low and high must be integers")

    validate_range(low, high)
    return random.randint(low, high)


def random_float(low: float = 0.0, high: float = 1.0) -> float:
    """Generate a random float between low and high.

    Args:
        low: Lower bound (default 0.0)
        high: Upper bound (default 1.0)

    Returns:
        Random float between low and high

    Raises:
        ValueError: If low > high
        TypeError: If inputs are not numeric
    """
    if not isinstance(low, int | float) or not isinstance(high, int | float):
        raise TypeError("Both low and high must be numeric")

    validate_range(low, high)
    return random.uniform(low, high)


def random_choices(
    population: list[Any], k: int = 1, weights: list[int | float] | None = None
) -> list[Any]:
    """Choose k items from population with replacement, optionally weighted.

    Args:
        population: List of items to choose from
        k: Number of items to choose (default 1)
        weights: Optional weights for each item (default None for equal weights)

    Returns:
        List of k chosen items

    Raises:
        ValueError: If population is empty, k < 0, or weights length doesn't match
        TypeError: If k is not an integer
    """
    validate_list_not_empty(population, "population")
    validate_positive_int(k, "k")

    if weights is not None:
        validate_weights_match_population(population, weights)

    return random.choices(population, weights=weights, k=k)


def random_shuffle(items: list[Any]) -> list[Any]:
    """Return a new list with items in random order.

    Args:
        items: List of items to shuffle

    Returns:
        New list with items in random order

    Raises:
        ValueError: If items list is empty
    """
    validate_list_not_empty(items, "items")

    # Use random.sample to return a new list instead of shuffling in place
    return random.sample(items, len(items))


def random_sample(population: list[Any], k: int) -> list[Any]:
    """Choose k unique items from population without replacement.

    Args:
        population: List of items to choose from
        k: Number of items to choose

    Returns:
        List of k unique chosen items

    Raises:
        ValueError: If population is empty, k < 0, or k > len(population)
        TypeError: If k is not an integer
    """
    validate_list_not_empty(population, "population")
    validate_positive_int(k, "k")
    if k > len(population):
        raise ValueError("Sample size k cannot be greater than population size")
    return random.sample(population, k)


def secure_token_hex(nbytes: int = 32) -> str:
    """Generate a secure random hex token.

    Args:
        nbytes: Number of random bytes to generate (default 32)

    Returns:
        Hex string containing 2*nbytes characters

    Raises:
        ValueError: If nbytes < 0
        TypeError: If nbytes is not an integer
    """
    validate_positive_int(nbytes, "nbytes")
    return secrets.token_hex(nbytes)


def secure_random_int(upper_bound: int) -> int:
    """Generate a secure random integer below upper_bound.

    Args:
        upper_bound: Upper bound (exclusive)

    Returns:
        Random integer in range [0, upper_bound)

    Raises:
        ValueError: If upper_bound <= 0
        TypeError: If upper_bound is not an integer
    """
    if not isinstance(upper_bound, int):
        raise TypeError("upper_bound must be an integer")

    if upper_bound <= 0:
        raise ValueError("upper_bound must be positive")

    return secrets.randbelow(upper_bound)
