"""
This module provides a class which represents a virtual load carrier.
"""

from dataclasses import dataclass
from typing import Optional

from bed_bpp_env.data_model.position_3d import Position3D


@dataclass
class LC(object):
    """
    Objects of this class represent represent different load carriers.
    """

    id: str
    """The id of the object."""
    sku: str
    """The SKU of the object."""
    type: Optional[str]
    """The type of the object."""

    length: int
    """The object's length in millimeters."""
    width: int
    """The object's width in millimeters."""
    height: int
    """The object's height in millimeters."""
    weight: Optional[float]
    """The object's weight in kilogramm."""

    position: Position3D
    """The position of the load carrier on a target."""

    @property
    def dimensions(self) -> tuple[int, int, int]:
        """The length, width, and height of the load carrier."""
        return self.length, self.width, self.height
