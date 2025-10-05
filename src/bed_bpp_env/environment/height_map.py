"""
Convenience class for representing the height of a Space3D.
"""

import utils

import matplotlib.pyplot as plt
import numpy as np
import logging

logger = logging.getLogger(__name__)


class HeightMap:
    """
    Convenience class for representing the height of a Space3D.

    Note that the np.arrays access the coordinates in (y, x) order.
    """

    def __init__(self, title: str = "HeightMap", size: tuple = (1200, 800), initialheight: int = 0) -> None:
        self.__TITLE = title
        """Defining the object for which this height map is created."""

        self.__INITIALHEIGHT = int(initialheight)
        """The initial height of the height map."""

        self.__SIZE = size
        """The size of the height map. Note that the first element is the size in x-direction and the second in y-direction. Thus, when creating a `np.array`, the elements have to be swapped."""

        self.__Heights = self.__INITIALHEIGHT * np.ones((int(self.__SIZE[1]), int(self.__SIZE[0])), dtype=int)
        """The heights on the target represented as `np.array`. Every unit is in millimeters."""

        self.shape = self.__Heights.shape
        """The shape of the height map. This is exactly the same as `np.shape`."""

        self.__PercentageSupportAreas = []
        """Defines how many percentage of an item bottom has direct support of its item below."""

    def __str__(self) -> str:
        prettyString = f"Visualization of {self.__TITLE}"
        for v in self.__Heights:
            printString = "{:<3} " * len(v)
            prettyString += "\n" + printString.format(*v)  # *v is needed to unpack the row
        return prettyString

    def reset(self, resize: tuple = (1200, 800)) -> None:
        """
        This method resets the attributes of (a) the stored heights and (b) the stored values of the support areas, to the initial values.

        Parameters.
        -----------
            resize: tuple (default = (1200, 800))
                The size of the height map. The first coordinate is the size in x-direction, the second in y-direction.
        """
        self.__SIZE = resize

        self.__Heights = self.__INITIALHEIGHT * np.ones((int(self.__SIZE[1]), int(self.__SIZE[0])), dtype=int)
        self.shape = self.__Heights.shape
        self.__PercentageSupportAreas = []

    def show(self) -> None:
        plt.imshow(self.__Heights, interpolation="nearest")
        plt.title(self.__TITLE)
        plt.show()

    def updateHeightMap(self, flbposition: tuple, other: "HeightMap") -> float:
        """Adds the height map of the item, starting at the FLB coordinates to the height map of a target."""
        flbCoordinates = [int(coord) for coord in flbposition]
        # define the ranges
        deltaY, deltaX = other.shape
        xStart, xEnd = flbCoordinates[0], flbCoordinates[0] + deltaX
        yStart, yEnd = flbCoordinates[1], flbCoordinates[1] + deltaY

        # calculate the percentage where the item has direct support
        idxAreaDirectSupport = np.argwhere(self.__Heights[yStart:yEnd, xStart:xEnd] == flbCoordinates[2])
        percentageDirectItemSupport = float(idxAreaDirectSupport.shape[0]) / float(deltaX * deltaY)
        self.__PercentageSupportAreas.append(percentageDirectItemSupport)
        # set all height values of the area where the item map is updated to the target z coordinate
        self.__Heights[yStart:yEnd, xStart:xEnd] = flbCoordinates[2] * np.ones((deltaY, deltaX), dtype=int)
        # add the height of the item
        self.__Heights[yStart:yEnd, xStart:xEnd] += other.getHeights()

        return percentageDirectItemSupport

    def getPercentageOfSupportAreas(self):
        """Returns the values of the supporting areas during palletization."""
        return self.__PercentageSupportAreas

    def getHeights(self) -> np.ndarray:
        return self.__Heights

    def getValues(self):
        return self.getHeights()

    def getValue(self, x, y) -> int:
        """Get the height value in (x,y)."""
        return self.__Heights[y, x]

    def setValue(self, x, y, val) -> None:
        """Sets the given value `val` to the idx (x,y) in the area."""
        self.__Heights[y, x] = val

    def getSubMap(self, startcoord, endcoord) -> np.ndarray:
        """Returns the requested part of the height map.

        Parameters.
        -----------
        startcoord: tuple
            Coordinates (x, y)
        endcoord: tuple
            Coordinates (x, y)
        """
        xStart, xEnd = startcoord[0], endcoord[0]
        yStart, yEnd = startcoord[1], endcoord[1]

        return self.__Heights[yStart:yEnd, xStart:xEnd]
