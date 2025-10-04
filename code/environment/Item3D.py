"""
Instances of this class represents cubic items that can be placed in a three-dimensional space, e.g., `environment.Space3D`.

One essential assumption we made here is that the items are placed parallel to the edges of the target!
"""

import logging
import numpy as np
from environment import HEIGHT_TOLERANCE_MM as HEIGHT_TOLERANCE_MM

logger = logging.getLogger(__name__)

PROPERTIES_DEFAULT_VALUE = -1
"""The default value that is set to an attribute whenever a key in the given properties is missing."""


class Item3D:
    """
    Instances of this class represents cubic items that can be placed in a three-dimensional space, e.g., `environment.Space3D`.

    Parameters.
    -----------
    properties: dict
        The properties of the item.
    """

    def __init__(self, properties: dict) -> None:
        self.__ID = properties.get("id", str(PROPERTIES_DEFAULT_VALUE))
        """This string is the ID of the item."""

        self.__Article = properties.get("article", str(PROPERTIES_DEFAULT_VALUE))
        """This string holds the article that is represented by this object."""
        self.__ProductGroup = properties.get("product_group", str(PROPERTIES_DEFAULT_VALUE))
        """This string holds the product group of the article that is represented by this object."""

        self.__DirectSupportSurface = None
        """This np.ndarray has exactly the same shape as the item and its values are in `[0, 1]`. A value of 1 represents direct support with the item below in this coordinate, otherwise the value is 0."""
        self.__PercentageDirectSupportSurface = None
        """A `float` that indicates how many percent of this object's base area has direct support from below. Values are in `[0, 1]`."""
        self.__EffectiveSupportSurface = None
        """The effective support surface of the item."""

        self.__ItemsBelow = []
        """Stores the items that are located below this object."""
        self.__Neighbors = {"north": [], "east": [], "south": [], "west": []}
        """Stores the items that are situated around this object."""

        self.__Weight = properties.get("weight/kg", PROPERTIES_DEFAULT_VALUE)
        """The weight of an item in [kg]."""

        self.__Length = int(properties.get("length/mm", PROPERTIES_DEFAULT_VALUE))
        """The length of the item in [mm]."""
        self.__Width = int(properties.get("width/mm", PROPERTIES_DEFAULT_VALUE))
        """The width of the item in [mm]."""
        self.__Height = int(properties.get("height/mm", PROPERTIES_DEFAULT_VALUE))
        """The height of the item in [mm]."""
        self.__Representation = self.__Height * np.ones((self.__Width, self.__Length), dtype=int)
        """A `np.ndarray` that represents the item. It has the shape of the item's base area size and its values are the height in millimeters."""

        self.__FLBCoordinates = None
        """A `list` that stores the front left bottom (FLB) coordinate of the item."""

    def setOrientation(self, value: int) -> None:
        """
        Sets the orientation of the item and thus, changes the shape of the representation.

        Parameters.
        -----------
        value: int
            The value of the item's orientation.
        """
        if value == 1:
            shape = self.__Representation.shape
            self.__Representation = self.__Representation.reshape((shape[1], shape[0]))
        elif value == 0:
            pass
        else:
            logger.warning(f'item "{self.__ID}" orientation: value {value} is not known! do nothing')

    def getOrientation(self) -> int:
        """
        Returns the orientation of an item.

        Returns.
        --------
        orientation: int
            Indicates whether the long edge is parallel to the long edge of the target or whether the item is rotated by 90 degrees.
        """
        shape = self.__Representation.shape

        if shape == (self.__Width, self.__Length):
            return 0
        elif shape == (self.__Length, self.__Width):
            return 1
        else:
            logger.warning(f'item "{self.__ID}" get orientation: not known! return None')
            return None

    def storeFLBCoordinates(self, coordinates: list) -> None:
        """Stores the FLB coordinates, e.g. `[x, y, z]`, of this object."""
        self.__FLBCoordinates = coordinates

    def storeItemsDirectlyBelow(self, items: list) -> None:
        """Sets the attribute that stores the items that are directly below this object."""
        self.__ItemsBelow = items

        self.__calculateDirectSupportSurface()
        self.__calculateEffectiveSupportSurface()

    def getDirectSupportSurface(self) -> np.ndarray:
        """
        Returns a np.ndarray that represents the areas where the item has direct support from below.

        Returns.
        --------
        __DirectSupportSurface: np.ndarray
            An array that shows where the item has direct support from below. The shape of this np.ndarray is identical to the item's shape; a value 1 represents direct support, 0 says no direct support.
        """
        return self.__DirectSupportSurface

    def getEffectiveSupportSurface(self) -> np.ndarray:
        """
        Returns a np.ndarray that represents the areas where the item has effective support.

        Returns.
        --------
        __EffectiveSupportSurface: np.ndarray
            An array that shows where the item has effective support. The shape of this np.ndarray is identical to the item's shape; a value 1 represents effective support, 0 says no effective support.
        """
        return self.__EffectiveSupportSurface

    def getPercentageDirectSupportSurface(self) -> float:
        """Returns the percentage of the bottom surface that has direct support to the item below."""
        # a value in [0, 1]
        return self.__PercentageDirectSupportSurface

    def getRepresentation(self) -> np.ndarray:
        """Returns the representation of the item."""
        return self.__Representation

    def getVolume(self) -> float:
        """Returns the volume of the item in mm^3."""
        return float(self.__Length * self.__Width * self.__Height)

    def getCoordinatesEdge(self, which: str) -> dict:
        """
        Returns the coordinates of the edge of an item when it is placed in an `Space3D`.

        On the edges, where either the x coordinate, or the y coordinate is only one number, also the value before is added to the coordinates set. E.g., if an item is located in (100,100,0), then the x coordinate for the west edge is `set([99, 100])`.


        Parameters.
        -----------
        which: str
            Defines for which edge you get the coordinates. Possible values are `"north"`, `"east"`, `"south"`, and `"west"`.

        Returns.
        --------
        coordinates: dict
            Key is either `x` or `y`, and the values are a set object that contains the values of the coordinates.
        """
        flbX, flbY, _ = self.__FLBCoordinates
        width, length = self.__Representation.shape

        if which == "north":
            coordinates = {"x": set(range(flbX, (flbX + length))), "y": set(range(flbY + width - 1, flbY + width + 1))}
        elif which == "east":
            coordinates = {"x": set(range(flbX + length - 1, flbX + length + 1)), "y": set(range(flbY, (flbY + width)))}
        elif which == "south":
            coordinates = {"x": set(range(flbX, (flbX + length))), "y": set(range(flbY - 1, flbY + 1))}
        elif which == "west":
            coordinates = {"x": set(range(flbX - 1, flbX + 1)), "y": set(range(flbY, (flbY + width)))}

        else:
            coordinates = {"x": set(), "y": set()}

        return coordinates

    def getCoordinatesHeightRange(self) -> set:
        """
        Returns the range of the z-coordinates of this item.

        Returns.
        --------
        zCoordinates: set
            The range of the x-coordinates of this item ({flb_z, ..., flb_z + height}).
        """
        _, _, flbZ = self.__FLBCoordinates
        height = self.__Representation[0, 0]
        return set(range(flbZ, flbZ + height))

    def getCoordinatesXRange(self) -> set:
        """
        Returns the range of the x-coordinates of this item.

        Returns.
        --------
        xCoordinates: set
            The range of the x-coordinates of this item ({flb_x, ..., flb_x + length}).
        """
        flbX, _, _ = self.__FLBCoordinates
        length = self.__Representation.shape[1]
        return set(range(flbX, flbX + length))

    def getCoordinatesYRange(self) -> set:
        """
        Returns the range of the y-coordinates of this item.

        Returns.
        --------
        yCoordinates: set
            The range of the y-coordinates of this item ({flb_y, ..., flb_y + width}).
        """
        _, flbY, _ = self.__FLBCoordinates
        width = self.__Representation.shape[0]
        return set(range(flbY, flbY + width))

    def getFLBCoordinates(self) -> list:
        """Returns the lbb coordinates of this item as list."""
        return self.__FLBCoordinates

    def getItemsBelow(self) -> list:
        """Returns the list of all items that are belowed this object."""
        return self.__ItemsBelow

    def getID(self) -> str:
        """Returns the ID of the item."""
        return self.__ID

    def storeNeighbors(self, neighbors: dict) -> None:
        """
        Stores the neighbors of this object and adds itself to its neighbors on the corresponding edge.

        Example.
        --------
        >>> neighbors = {
            "north": [environment.Item3D object],
            "east": [],
            "south": [],
            "west": []
        }
        """
        self.__Neighbors = neighbors

        # edgeNeighbor = EDGE_MAPPER[edge_self]
        EDGE_MAPPER = {"north": "south", "east": "west", "south": "north", "west": "east"}

        for edgeSelf, neighborList in neighbors.items():
            for neighbor in neighborList:
                neighbor.addNeighbor(EDGE_MAPPER[edgeSelf], self)

        logger.debug(f'item "{self.__ID}" neighbors: {self.__Neighbors}')

    def addNeighbor(self, edge: str, neighbor: "Item3D") -> None:
        """
        Adds the given neighbor to the defined edge to this object's neighbors.

        Parameters.
        -----------
        edge: str
            On which edge have `self` and `neighbor` contact. Values can be `"north"`, `"east"`, `"south"`, or `"west"`.
        neighbor: Item3D
            The neighbor that is added to this object.
        """
        if not (neighbor in self.__Neighbors[edge]):
            self.__Neighbors[edge].append(neighbor)

    def getNeighbors(self) -> dict:
        """
        Returns the neighbors in each direction of this object.

        Example.
        --------
        >>> Item3D.getNeighbors()
        {
            "north": [environment.Item3D object],
            "east": [],
            "south": [],
            "west": []
        }
        """
        return self.__Neighbors

    def __calculateDirectSupportSurface(self) -> None:
        if self.__ItemsBelow == []:
            # object is directly located on palletizing target
            self.__PercentageDirectSupportSurface = 1.0
            self.__DirectSupportSurface = np.ones(self.__Representation.shape, dtype=int)

        else:
            self.__PercentageDirectSupportSurface = 0.0  # initial value
            self.__DirectSupportSurface = np.zeros(self.__Representation.shape, dtype=int)

            selfCoordinatesX, selfCoordinatesY = self.getCoordinatesXRange(), self.getCoordinatesYRange()
            for itemBelow in self.__ItemsBelow:
                overlappingPointsX = set.intersection(selfCoordinatesX, itemBelow.getCoordinatesXRange())
                overlappingPointsY = set.intersection(selfCoordinatesY, itemBelow.getCoordinatesYRange())

                self.__PercentageDirectSupportSurface += (len(overlappingPointsX) * len(overlappingPointsY)) / (
                    self.__Representation.shape[0] * self.__Representation.shape[1]
                )

                # create the DirectSupportSurface ndarray
                startX, startY = (
                    min(overlappingPointsX) - self.__FLBCoordinates[0],
                    min(overlappingPointsY) - self.__FLBCoordinates[1],
                )
                endX, endY = (
                    max(overlappingPointsX) - self.__FLBCoordinates[0] + 1,
                    max(overlappingPointsY) - self.__FLBCoordinates[1] + 1,
                )

                self.__DirectSupportSurface[startY:endY, startX:endX] = np.ones(
                    (endY - startY, endX - startX), dtype=int
                )

        logger.debug(f'item "{self.__ID}" direct support surface(%): {self.__PercentageDirectSupportSurface}')

    def __calculateEffectiveSupportSurface(self) -> None:
        if self.__ItemsBelow == []:
            self.__EffectiveSupportSurface = self.__DirectSupportSurface.copy()

        else:
            self.__EffectiveSupportSurface = np.zeros(self.__Representation.shape, dtype=int)

            selfCoordinatesX, selfCoordinatesY = self.getCoordinatesXRange(), self.getCoordinatesYRange()
            for itemBelow in self.__ItemsBelow:
                overlappingPointsX = set.intersection(selfCoordinatesX, itemBelow.getCoordinatesXRange())
                overlappingPointsY = set.intersection(selfCoordinatesY, itemBelow.getCoordinatesYRange())

                # create the DirectSupportSurface ndarray
                startX, startY = (
                    min(overlappingPointsX) - self.__FLBCoordinates[0],
                    min(overlappingPointsY) - self.__FLBCoordinates[1],
                )
                endX, endY = (
                    max(overlappingPointsX) - self.__FLBCoordinates[0] + 1,
                    max(overlappingPointsY) - self.__FLBCoordinates[1] + 1,
                )

                self.__EffectiveSupportSurface[startY:endY, startX:endX] = np.ones(
                    (endY - startY, endX - startX), dtype=int
                )

            if len(self.__ItemsBelow) > 1:
                # multi package support => change corners
                coordsEffectiveSupportSurface = np.argwhere(self.__EffectiveSupportSurface >= 1)

                min1stCoord = np.amin(coordsEffectiveSupportSurface[:, 0])  # min first coord
                max1stCoord = np.amax(coordsEffectiveSupportSurface[:, 0])  # max first coord

                candMin1Extr2 = np.where(
                    coordsEffectiveSupportSurface[:, 0] == min1stCoord, coordsEffectiveSupportSurface[:, 1], np.nan
                )
                min1stMax2nd = int(np.nanmax(candMin1Extr2))
                min1stMin2nd = int(np.nanmin(candMin1Extr2))

                candMax1Extr2 = np.where(
                    coordsEffectiveSupportSurface[:, 0] == max1stCoord, coordsEffectiveSupportSurface[:, 1], np.nan
                )
                max1stMax2nd = int(np.nanmax(candMax1Extr2))
                max1stMin2nd = int(np.nanmin(candMax1Extr2))

                point1 = [min1stCoord, min1stMin2nd]
                point2 = [min1stCoord, min1stMax2nd]
                point3 = [max1stCoord, max1stMax2nd]
                point4 = [max1stCoord, max1stMin2nd]

                startX = min(point1[1], point4[1])
                startY = min(point1[0], point2[0])

                endX = max(point2[1], point3[1]) + 1
                endY = max(point3[0], point4[0]) + 1

                self.__EffectiveSupportSurface[startY:endY, startX:endX] = np.ones(
                    (endY - startY, endX - startX), dtype=int
                )
            else:
                # single package support
                self.__EffectiveSupportSurface = np.multiply(
                    self.__EffectiveSupportSurface, self.__DirectSupportSurface
                )

    def getHeight(self) -> int:
        """Returns the height of the item."""
        return self.__Height
