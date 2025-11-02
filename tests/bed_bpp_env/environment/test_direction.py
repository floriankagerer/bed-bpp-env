"""Tests the module `direction`."""

import pytest
from bed_bpp_env.environment.direction import Direction, opposite_direction


def test_direction_is_str_enum() -> None:
    for direction in Direction:
        assert isinstance(direction.value, str)


def test_direction_from_value() -> None:
    """Tests whether we can create a `Direction` from a value."""
    test_cases = [
        ("north", Direction.NORTH),
        ("east", Direction.EAST),
        ("south", Direction.SOUTH),
        ("west", Direction.WEST),
    ]

    for value, expected_direction in test_cases:
        actual_direction = Direction(value)

        assert actual_direction is expected_direction


def test_direction_raises_error_from_invalid_value() -> None:
    """Tests that an exception is raised if a `Direction` is created from an invalid value."""
    with pytest.raises(ValueError):
        Direction("invalid-direction")


def test_opposite_direction() -> None:
    """Tests whether the correct opposite direction is returned."""

    test_cases = [
        (Direction.NORTH, Direction.SOUTH),
        (Direction.EAST, Direction.WEST),
        (Direction.SOUTH, Direction.NORTH),
        (Direction.WEST, Direction.EAST),
    ]

    for direction, expected_opposite in test_cases:
        actual_opposite = opposite_direction(direction=direction)

        assert actual_opposite is expected_opposite
