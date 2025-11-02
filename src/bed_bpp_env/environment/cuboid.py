"""
Instances of this class represents cubic items that can be placed in a three-dimensional space, e.g., `Space3D`.

One essential assumption we made here is that the items are placed parallel to the edges of the target!
"""

import logging
from typing import Optional, Self

import numpy as np

from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.position_3d import Position3D

logger = logging.getLogger(__name__)


class Cuboid(object):
    """
    Instances of this class represents cubic items that can be placed in a three-dimensional space, e.g., `Space3D`.

    Parameters.
    -----------
    properties: dict
        The properties of the item.
    """

    def __init__(self, metadata: Item) -> None:
        self._metadata = metadata

        self._direct_support_surface = None
        """This np.ndarray has exactly the same shape as the item and its values are in `[0, 1]`. A value of `1` 
        represents direct support with the item below in this coordinate, otherwise the value is `0`."""
        self._percentage_direct_support_surface: Optional[float] = None
        """A `float` that indicates how many percent of this object's base area has direct support from below. Values are in `[0, 1]`."""
        self._effective_support_surface = None
        """The effective support surface of the item."""

        self._items_below: list[Self] = []
        """Stores the items that are located below this object."""
        # TODO(florian): implement module for neighbor, enum for direction.
        self._neighbors = {"north": [], "east": [], "south": [], "west": []}
        """Stores the items that are situated around this object."""

        self._representation = self.height * np.ones((self.width, self.length), dtype=int)
        """A `np.ndarray` that represents the item. It has the shape of the item's base area size and its values are the height in millimeters."""

        self._flb_coordinates = None
        """A `list` that stores the front left bottom (FLB) coordinate of the item."""

    @property
    def id(self) -> str:
        """The identifier of this cuboid."""
        return self._metadata.id

    @property
    def length(self) -> int:
        """The length of this cuboid."""
        return int(self._metadata.length_mm)

    @property
    def width(self) -> int:
        """The width of this cuboid."""
        return int(self._metadata.width_mm)

    @property
    def height(self) -> int:
        """The height of this cuboid."""
        return self._metadata.height_mm

    @property
    def weight(self) -> float:
        """The weight of this cuboid."""
        return self._metadata.weight_kg

    @property
    def volume(self) -> float:
        """The volume of this cuboid."""
        return float(self.length * self.width * self.height)

    @property
    def flb(self) -> Position3D:
        """The front left bottom (FLB) coordinates of this cuboid."""
        return self._flb_coordinates

    @flb.setter
    def flb(self, position: Position3D) -> None:
        self._flb_coordinates = position

    @property
    def direct_support_surface(self) -> np.ndarray:
        """This np.ndarray has exactly the same shape as the item and its values are in `[0, 1]`. A value of 1
        represents direct support with the item below in this coordinate, otherwise the value is 0."""
        return self._direct_support_surface

    @property
    def percentage_direct_support_surface(self) -> float:
        """Returns the percentage, i.e., a value in [0, 1], of the bottom surface that has direct support
        to the item below."""
        return self._percentage_direct_support_surface

    @property
    def effective_support_surface(self) -> np.ndarray:
        """An array that shows where the item has effective support. The shape of this array is identical to the
        item's shape; a value `1` represents effective support, `0` says no effective support."""
        return self._effective_support_surface

    @property
    def neighbors(self) -> dict[str, list[Self]]:
        """
        The neighbors in each direction of this cuboid.

        # TODO(florian): Remove example once tests are implemented.
        Example.
        --------
        >>> cuboid.getNeighbors()
        {
            "north": [Cuboid object],
            "east": [],
            "south": [],
            "west": []
        }
        """
        return self._neighbors

    @property
    def items_below(self) -> list[Self]:
        """Returns the list of all items that are belowed this object."""
        return self._items_below

    def set_orientation(self, value: int) -> None:
        """
        Sets the orientation of the item and thus, changes the shape of the representation.

        Parameters.
        -----------
        value: int
            The value of the item's orientation.
        """
        if value == 1:
            shape = self._representation.shape
            self._representation = self._representation.reshape((shape[1], shape[0]))
        elif value == 0:
            pass
        else:
            logger.warning(f'item "{self.id}" orientation: value {value} is not known! do nothing')

    @property
    def orientation(self) -> int:
        """
        The orientation of an item.

        Returns.
        --------
        orientation: int
            Indicates whether the long edge is parallel to the long edge of the target or whether the item is rotated by 90 degrees.
        """
        shape = self._representation.shape

        if shape == (self.width, self.length):
            return 0
        elif shape == (self.length, self.width):
            return 1
        else:
            logger.warning(f'item "{self.id}" get orientation: not known! return None')
            return None

    def store_items_directly_below(self, items: list[Self]) -> None:
        """Sets the attribute that stores the items that are directly below this object."""
        self._items_below = items

        self._calculate_direct_support_surface()
        self._calculate_effective_support_surface()

    @property
    def array_representation(self) -> np.ndarray:
        """The item represented as array."""
        return self._representation

    def coordinates_ranges_of_edge(self, which: str) -> dict[str, set[int]]:
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
        flb_x = self.flb.x
        flb_y = self.flb.y
        width, length = self._representation.shape

        if which == "north":
            coordinates = {
                "x": set(range(flb_x, (flb_x + length))),
                "y": set(range(flb_y + width - 1, flb_y + width + 1)),
            }
        elif which == "east":
            coordinates = {
                "x": set(range(flb_x + length - 1, flb_x + length + 1)),
                "y": set(range(flb_y, (flb_y + width))),
            }
        elif which == "south":
            coordinates = {
                "x": set(range(flb_x, (flb_x + length))),
                "y": set(range(flb_y - 1, flb_y + 1)),
            }
        elif which == "west":
            coordinates = {
                "x": set(range(flb_x - 1, flb_x + 1)),
                "y": set(range(flb_y, (flb_y + width))),
            }

        else:
            coordinates = {"x": set(), "y": set()}

        return coordinates

    @property
    def coordinates_z_range(self) -> set[int]:
        """
        Returns the range of the z-coordinates of this item.

        Returns.
        --------
        zCoordinates: set
            The range of the x-coordinates of this item ({flb_z, ..., flb_z + height}).
        """
        flb_z = self.flb.z
        height = self._representation[0, 0]
        return set(range(flb_z, flb_z + height))

    @property
    def coordinates_x_range(self) -> set[int]:
        """
        Returns the range of the x-coordinates of this item.

        Returns.
        --------
        xCoordinates: set
            The range of the x-coordinates of this item ({flb_x, ..., flb_x + length}).
        """
        flb_x = self.flb.x
        length = self._representation.shape[1]
        return set(range(flb_x, flb_x + length))

    @property
    def coordinates_y_range(self) -> set[int]:
        """
        Returns the range of the y-coordinates of this item.

        Returns.
        --------
        yCoordinates: set
            The range of the y-coordinates of this item ({flb_y, ..., flb_y + width}).
        """
        flb_y = self.flb.y
        width = self._representation.shape[0]
        return set(range(flb_y, flb_y + width))

    def store_neighbors(self, neighbors: dict[str, list[Self]]) -> None:
        """
        Stores the neighbors of this object and adds itself to its neighbors on the corresponding edge.

        Example.
        --------
        >>> neighbors = {
            "north": [Cuboid object],
            "east": [],
            "south": [],
            "west": []
        }
        """
        self._neighbors = neighbors

        # TODO(florian): This edge mapper belongs in the direction module, e.g., opposite_direction
        EDGE_MAPPER = {"north": "south", "east": "west", "south": "north", "west": "east"}

        for edge_self, edge_neighbors in neighbors.items():
            for neighbor in edge_neighbors:
                neighbor.add_neighbor(EDGE_MAPPER[edge_self], self)

        logger.debug(f'item "{self.id}" neighbors: {self._neighbors}')

    def add_neighbor(self, edge: str, neighbor: Self) -> None:
        """
        Adds the given neighbor to the defined edge to this object's neighbors.

        Parameters.
        -----------
        edge: str
            On which edge have `self` and `neighbor` contact. Values can be `"north"`, `"east"`, `"south"`, or `"west"`.
        neighbor: Cuboid
            The neighbor that is added to this object.
        """
        if neighbor not in self._neighbors[edge]:
            self._neighbors[edge].append(neighbor)

    def _calculate_direct_support_surface(self) -> None:
        if self._items_below == []:
            # object is directly located on palletizing target
            self._percentage_direct_support_surface = 1.0
            self._direct_support_surface = np.ones(self._representation.shape, dtype=int)

        else:
            self._percentage_direct_support_surface = 0.0  # initial value
            self._direct_support_surface = np.zeros(self._representation.shape, dtype=int)

            self_coordinate_x, self_coordinate_y = self.coordinates_x_range, self.coordinates_y_range
            for item_below in self._items_below:
                overlapping_points_x = set.intersection(self_coordinate_x, item_below.coordinates_x_range)
                overlapping_points_y = set.intersection(self_coordinate_y, item_below.coordinates_y_range)

                self._percentage_direct_support_surface += (len(overlapping_points_x) * len(overlapping_points_y)) / (
                    self._representation.shape[0] * self._representation.shape[1]
                )

                # create the DirectSupportSurface ndarray
                start_x, start_y = (
                    min(overlapping_points_x) - self.flb.x,
                    min(overlapping_points_y) - self.flb.y,
                )
                end_x, end_y = (
                    max(overlapping_points_x) - self.flb.x + 1,
                    max(overlapping_points_y) - self.flb.y + 1,
                )

                self._direct_support_surface[start_y:end_y, start_x:end_x] = np.ones(
                    (end_y - start_y, end_x - start_x), dtype=int
                )

        logger.debug(f'item "{self.id}" direct support surface(%): {self._percentage_direct_support_surface}')

    def _calculate_effective_support_surface(self) -> None:
        if self._items_below == []:
            self._effective_support_surface = self._direct_support_surface.copy()

        else:
            self._effective_support_surface = np.zeros(self._representation.shape, dtype=int)

            self_coordinate_x, self_coordinate_y = self.coordinates_x_range, self.coordinates_y_range
            for item_below in self._items_below:
                overlapping_points_x = set.intersection(self_coordinate_x, item_below.coordinates_x_range)
                overlapping_points_y = set.intersection(self_coordinate_y, item_below.coordinates_y_range)

                # create the DirectSupportSurface ndarray
                start_x, start_y = (
                    min(overlapping_points_x) - self.flb.x,
                    min(overlapping_points_y) - self.flb.y,
                )
                end_x, end_y = (
                    max(overlapping_points_x) - self.flb.x + 1,
                    max(overlapping_points_y) - self.flb.y + 1,
                )

                self._effective_support_surface[start_y:end_y, start_x:end_x] = np.ones(
                    (end_y - start_y, end_x - start_x), dtype=int
                )

            if len(self._items_below) > 1:
                # multi package support => change corners
                coords_effective_support_surface = np.argwhere(self._effective_support_surface >= 1)

                min_1st_coord = np.amin(coords_effective_support_surface[:, 0])  # min first coord
                max_1st_coord = np.amax(coords_effective_support_surface[:, 0])  # max first coord

                cand_min1_extr2 = np.where(
                    coords_effective_support_surface[:, 0] == min_1st_coord,
                    coords_effective_support_surface[:, 1],
                    np.nan,
                )
                min_1st_max_2nd = int(np.nanmax(cand_min1_extr2))
                min_1st_min_2nd = int(np.nanmin(cand_min1_extr2))

                cand_max1_extr2 = np.where(
                    coords_effective_support_surface[:, 0] == max_1st_coord,
                    coords_effective_support_surface[:, 1],
                    np.nan,
                )
                max_1st_max_2nd = int(np.nanmax(cand_max1_extr2))
                max_1st_min_2nd = int(np.nanmin(cand_max1_extr2))

                point1 = [min_1st_coord, min_1st_min_2nd]
                point2 = [min_1st_coord, min_1st_max_2nd]
                point3 = [max_1st_coord, max_1st_max_2nd]
                point4 = [max_1st_coord, max_1st_min_2nd]

                start_x = min(point1[1], point4[1])
                start_y = min(point1[0], point2[0])

                end_x = max(point2[1], point3[1]) + 1
                end_y = max(point3[0], point4[0]) + 1

                self._effective_support_surface[start_y:end_y, start_x:end_x] = np.ones(
                    (end_y - start_y, end_x - start_x), dtype=int
                )
            else:
                # single package support
                self._effective_support_surface = np.multiply(
                    self._effective_support_surface, self._direct_support_surface
                )
