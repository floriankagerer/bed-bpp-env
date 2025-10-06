"""
This module provides a class which represents a virtual load carrier.
"""

from dataclasses import dataclass
from typing import Optional


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

    position: dict
    """The position of the load carrier on a target."""

    # TODO(florian): Define dataclass for position
    # self.__Targetposition = {
    #     "area": None,
    #     "x": 0,  # on target
    #     "y": 0,  # on target
    #     "z": 0,  # on target
    # }

    @property
    def dimensions(self) -> tuple[int, int, int]:
        """The length, width, and height of the load carrier."""
        return self.length, self.width, self.height
