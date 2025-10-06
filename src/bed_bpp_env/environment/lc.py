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

    def getProperties(self) -> dict:
        """Returns the properties of the load carrier as dictionary."""
        length, width, height = self.getDimensions()
        lcProps = {
            "cont_id": self.id,
            "sku": self.getSKU(),
            "lc_type": self.getLCType(),
            "length": length,
            "width": width,
            "height": height,
            "weigth": self.getWeight(),
            "target_pos": self.getTargetposition(),
        }
        return lcProps

    def getLCType(self) -> str:
        """Returns the load carrier type."""
        return self.type

    def getHeight(self) -> int:
        """Returns the height of the load carrier."""
        return self.height

    def getWeight(self) -> float:
        """Returns the weight of the load carrier."""
        return self.weight

    def getSKU(self) -> str:
        """Returns the SKU of the load carrier."""
        return self.sku

    def getDimensions(self) -> list:
        """Returns the length, width and height of the load carrier as a list."""
        return [self.length, self.width, self.height].copy()

    def getTargetposition(self, coordinate=None):
        """
        Returns the target position of the load carrier. If the parameter `coordinate` is specfied, the requested coordinate is returned.

        Parameters.
        -----------
        coordinate: str (default: None)
            Possible values are "x", "y", "z" and "area".

        Returns.
        --------
        target: dict
            The target position of the object, i.e., a dictionary with the keys 'area', 'x', 'y' and 'z'.
        OR
        coordinate: int
            The requested coordinate.
        """
        if coordinate is None:
            # return a copy of the targetposition coordinates
            return self.position.copy()
        else:
            # return the specified coordinate
            return self.position.copy()[coordinate]

    def getVolume(self) -> float:
        """Calculates the volume of the LC in [mm^3] and returns it as float."""
        return float(self.length * self.width * self.height)

    def setTargetposition(self, target: dict) -> None:
        """
        Sets the targetposition of the load carrier.

        Parameters.
        -----------
        target: dict
            The target position of the object, i.e., a dictionary with the keys 'area', 'x', 'y' and 'z'.
        """
        self.position["area"] = target["area"]
        self.position["x"] = target["x"]
        self.position["y"] = target["y"]
        self.position["z"] = target["z"]
