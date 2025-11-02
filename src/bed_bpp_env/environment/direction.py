from enum import StrEnum


class Direction(StrEnum):
    """Represents directions."""

    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"


def opposite_direction(direction: Direction) -> Direction:
    """Returns the opposite direction of the given direction.

    Args:
        direction (Direction): The direction for that the opposite direction is returned.

    Returns:
        Direction: The opposite direction.
    """
    if direction is Direction.NORTH:
        return Direction.SOUTH

    elif direction is Direction.EAST:
        return Direction.WEST

    elif direction is Direction.SOUTH:
        return Direction.NORTH

    elif direction is Direction.WEST:
        return Direction.EAST

    raise ValueError("direction is not recognized")
