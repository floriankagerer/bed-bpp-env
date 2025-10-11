"""Contains a class that represents a position in 3D."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Optional

SERIALIZE_NONE = False
"""Indicates whether `None` values are serialized."""


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

    def to_dict(self) -> dict[str, str | int | None]:
        """Converts the object to a dictionary."""
        position_to_dict = {}

        for position_field in fields(self):
            key = position_field.name
            value = getattr(self, position_field.name)

            if not SERIALIZE_NONE and value is None:
                continue

            position_to_dict[key] = value

        return position_to_dict

    @classmethod
    def from_dict(cls, serialized: dict[str, str | int | None]) -> Position3D:
        """Deserialize dictionary into dataclass instance."""
        return cls(**serialized)
