"""Contains a class that represents a position in 3D."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position3D(object):
    """A position in 3d with an optional area name."""

    x: int
    """The x-coordinate of the position."""
    y: int
    """The y-coordinate of the position."""
    z: int
    """The z-coordinate of the position."""
    area: Optional[str] = None
    """An optional name of the area this position belongs to."""

    @property
    def xyz(self) -> tuple[int, int, int]:
        """The position given as `(x, y, z)`."""
        return self.x, self.y, self.z
