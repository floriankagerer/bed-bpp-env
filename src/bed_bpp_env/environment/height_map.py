"""
Convenience class for representing the height of a Space3D.
"""

import logging

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


class HeightMap:
    """
    Convenience class for representing the height of a Space3D.

    Note that the np.arrays access the coordinates in (y, x) order.
    """

    def __init__(self, title: str = "HeightMap", size: tuple = (1200, 800), initialheight: int = 0) -> None:
        self._title = title
        """Defining the object for which this height map is created."""

        self._initial_height = int(initialheight)
        """The initial height of the height map."""

        self._size = size
        """The size of the height map. Note that the first element is the size in x-direction and the second in y-direction. Thus, when creating a `np.array`, the elements have to be swapped."""

        self._heights = self._initial_height * np.ones((int(self._size[1]), int(self._size[0])), dtype=int)
        """The heights on the target represented as `np.array`. Every unit is in millimeters."""

        self.shape = self._heights.shape
        """The shape of the height map. This is exactly the same as `np.shape`."""

        self._percentage_support_surface = []
        """Defines how many percentage of an item bottom has direct support of its item below."""

    def __str__(self) -> str:
        pretty_string = f"Visualization of {self._title}"
        for v in self._heights:
            print_string = "{:<3} " * len(v)
            pretty_string += "\n" + print_string.format(*v)  # *v is needed to unpack the row
        return pretty_string

    def reset(self, resize: tuple = (1200, 800)) -> None:
        """
        This method resets the attributes of (a) the stored heights and (b) the stored values of the support areas, to the initial values.

        Parameters.
        -----------
            resize: tuple (default = (1200, 800))
                The size of the height map. The first coordinate is the size in x-direction, the second in y-direction.
        """
        self._size = resize

        self._heights = self._initial_height * np.ones((int(self._size[1]), int(self._size[0])), dtype=int)
        self.shape = self._heights.shape
        self._percentage_support_surface = []

    def show(self) -> None:
        plt.imshow(self._heights, interpolation="nearest")
        plt.title(self._title)
        plt.show()

    def updateHeightMap(self, flbposition: tuple, other: "HeightMap") -> float:
        """Adds the height map of the item, starting at the FLB coordinates to the height map of a target."""
        flb_coordinates = [int(coord) for coord in flbposition]
        # define the ranges
        delta_y, delta_x = other.shape
        x_start, x_end = flb_coordinates[0], flb_coordinates[0] + delta_x
        y_start, y_end = flb_coordinates[1], flb_coordinates[1] + delta_y

        # calculate the percentage where the item has direct support
        idx_area_direct_support = np.argwhere(self._heights[y_start:y_end, x_start:x_end] == flb_coordinates[2])
        percentage_direct_item_support = float(idx_area_direct_support.shape[0]) / float(delta_x * delta_y)
        self._percentage_support_surface.append(percentage_direct_item_support)
        # set all height values of the area where the item map is updated to the target z coordinate
        self._heights[y_start:y_end, x_start:x_end] = flb_coordinates[2] * np.ones((delta_y, delta_x), dtype=int)
        # add the height of the item
        self._heights[y_start:y_end, x_start:x_end] += other.getHeights()

        return percentage_direct_item_support

    def getPercentageOfSupportAreas(self):
        """Returns the values of the supporting areas during palletization."""
        return self._percentage_support_surface

    def getHeights(self) -> np.ndarray:
        return self._heights

    def getValues(self):
        return self.getHeights()

    def getValue(self, x, y) -> int:
        """Get the height value in (x,y)."""
        return self._heights[y, x]

    def setValue(self, x, y, val) -> None:
        """Sets the given value `val` to the idx (x,y) in the area."""
        self._heights[y, x] = val

    def getSubMap(self, startcoord, endcoord) -> np.ndarray:
        """Returns the requested part of the height map.

        Parameters.
        -----------
        startcoord: tuple
            Coordinates (x, y)
        endcoord: tuple
            Coordinates (x, y)
        """
        x_start, x_end = startcoord[0], endcoord[0]
        y_start, y_end = startcoord[1], endcoord[1]

        return self._heights[y_start:y_end, x_start:x_end]
