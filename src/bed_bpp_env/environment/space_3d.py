"""
This module contains a class that represents a virtual, three-dimensional space.
"""

import logging

import numpy as np

from bed_bpp_env.data_model.position_3d import Position3D
from bed_bpp_env.environment import HEIGHT_TOLERANCE_MM as HEIGHT_TOLERANCE_MM
from bed_bpp_env.environment.cuboid import Cuboid

logger = logging.getLogger(__name__)

MAXHEIGHT = 3_000  # for corner points
"""The maximum height in millimeters for that corner points are determined. Needs to be greater than the maximum palletizing height."""


class Space3D:
    """
    This class represents a virtual space to which items are added.
    describe class Space3D

    Parameters.
    -----------
    basesize: tuple (default = (1200, 800))
        The space's size of the base area in x- and y-direction given in millimeters.

    Attributes.
    -----------
    _heights: np.ndarray
        'This `np.ndarray` has the shape of the palletizing target and stores the height in each position in millimeters.
    _placed_items: dict
        This dictionary's keys are the chronological order of the placed items and its values are the items as `Item3D` object.
    _size: tuple
       The space's size of the base area in x- and y-direction given in millimeters.
    _uppermost_items:  np.ndarray
        This `np.ndarray` has the same shape as the height map of the three-dimensional space and stores a counter that represents the counter of the uppermost item.
    """

    def __init__(self, basesize: tuple = (1_200, 8_00)) -> None:
        self._size = basesize
        """The space's size of the base area in x- and y-direction given in millimeters."""

        self._placed_items = {}
        """This dictionary's keys are the chronological order of the placed items and its values are the items as `Item3D` object."""

        target_shape = self._size[1], self._size[0]
        self._heights = np.zeros(target_shape, dtype=int)
        """This `np.ndarray` has the shape of the palletizing target and stores the height in each position in millimeters."""

        self._uppermost_items = np.zeros(target_shape, dtype=int)
        """This `np.ndarray` has the same shape as the height map of the three-dimensional space and stores a counter that represents the counter of the uppermost item."""

    def getPlacedItems(self) -> list[Cuboid]:
        """Returns all placed items as list of `Item3D`."""
        return list(self._placed_items.values())

    def addItem(self, item: Cuboid, orientation: int, flbcoordinates: list) -> None:
        """
        Adds an item to the virtual three-dimensional space and calculates the required attributes for the stability check evaluation.

        Parameters.
        -----------
        item: Item3D
            The item that is added to the space.
        orientation: int
            The orientation of the item.
        flbcoordinates: list
            The FLB coordinates in which the item is placed.
        """
        item.flb = Position3D(x=flbcoordinates[0], y=flbcoordinates[1], z=flbcoordinates[2])

        item_as_array = item.getRepresentation()
        # define the area where the item is located
        start_x, start_y = flbcoordinates[0], flbcoordinates[1]
        delta_x, delta_y = item_as_array.shape[1], item_as_array.shape[0]
        end_x, end_y = start_x + delta_x, start_y + delta_y

        # detect all items that directly support the current item
        items_area_below = self._uppermost_items[start_y:end_y, start_x:end_x]
        heights_area_below = self._heights[start_y:end_y, start_x:end_x]
        height_threshold = flbcoordinates[2] - HEIGHT_TOLERANCE_MM
        items_with_direct_support = np.where(heights_area_below >= height_threshold, items_area_below, -1)
        allItemsBelow = np.unique(items_with_direct_support)
        # remove item counter 0 <=> palletizing target
        # needed condition item <= len(placed items) because strange errors sometimes occured during dev
        counters_direct_items_below = [
            item for item in allItemsBelow if ((item > 0) and (item <= len(self._placed_items)))
        ]
        # obtain the Item3D objects and store it in the current item
        items_directly_below = [self._placed_items[countItem] for countItem in counters_direct_items_below]
        item.storeItemsDirectlyBelow(items_directly_below)

        # detect all neighbors of the current item
        target_size_y, target_size_x = self._uppermost_items.shape
        neighbor_start_x = start_x if start_x == 0 else start_x - 1
        neighbor_end_x = end_x if end_x == target_size_x - 1 else end_x + 1
        neighbor_start_y = start_y if start_y == 0 else start_y - 1
        neighbor_end_y = end_y if end_y == target_size_y - 1 else end_y + 1
        # create np.ndarray with items and heights
        items_area_neighbor = self._uppermost_items[neighbor_start_y:neighbor_end_y, neighbor_start_x:neighbor_end_x]
        heights_area_neighbor = self._heights[neighbor_start_y:neighbor_end_y, neighbor_start_x:neighbor_end_x]

        height_threshold = flbcoordinates[2]  # -HEIGHT_TOLERANCE_MM
        items_surround = np.where(heights_area_neighbor > height_threshold, items_area_neighbor, -1)
        all_items_surround = np.unique(items_surround)
        # # remove item counter 0 <=> palletizing target
        counters_possible_neighbor_items = [
            item for item in all_items_surround if item > 0 and (item not in items_directly_below)
        ]
        # # obtain the Item3D objects and store it in the current item
        possible_neighbors = [self._placed_items[countItem] for countItem in counters_possible_neighbor_items]
        self.__identifyNeighbors(item, possible_neighbors)

        # update the heights attribute
        crop = ""
        if end_x - start_x > self._heights.shape[1] - start_x:
            logger.warning("crop item in X direction")
            end_x = self._heights.shape[1]
            crop += "x"
        if end_y - start_y > self._heights.shape[0] - start_y:
            logger.warning("crop item in Y direction")
            end_y = self._heights.shape[0]
            crop += "y"
        self._heights[start_y:end_y, start_x:end_x] = flbcoordinates[2] * np.ones(
            (end_y - start_y, end_x - start_x), dtype=int
        )
        self._heights[start_y:end_y, start_x:end_x] += item_as_array[: end_y - start_y, : end_x - start_x]

        # update the uppermost items attribute and the placed items
        counter_item = len(self._placed_items) + 1
        self._uppermost_items[start_y:end_y, start_x:end_x] = counter_item * np.ones(
            (end_y - start_y, end_x - start_x), dtype=int
        )
        self._placed_items[counter_item] = item

    def reset(self, basesize: tuple) -> None:
        """
        Resets the attributes to their initial values and reshapes the numpy.ndarrays that store the heights and uppermost items.

        Parameters.
        -----------
        basesize: tuple
            The shape of the base area given as `(shape_x, shape_y)`.
        """
        self._size = basesize
        target_shape = self._size[1], self._size[0]

        self._placed_items = {}
        self._heights = np.zeros(target_shape, dtype=int)
        self._uppermost_items = np.zeros(target_shape, dtype=int)

    def getHeights(self) -> np.ndarray:
        """Returns the heights in millimeters in each coordinate of the space."""
        return self._heights

    def getItemsAboveHeightLevel(self, heightlevel: int) -> int:
        """
        Returns the amount of items that are located above the given height.

        Parameters.
        -----------
        heightlevel: int
            The height on the target in millimeters for that defines which items are counted as unpalletized.

        Returns.
        --------
        n_items_about_height_level: int
            The items that are located above a certain height level.
        """
        n_items_about_height_level = 0
        for item in self.getPlacedItems():
            if min(item.getCoordinatesHeightRange()) > heightlevel:
                n_items_about_height_level += 1

        return n_items_about_height_level

    def getMaximumHeightBelowHeightLevel(self, heightlevel: int) -> int:
        """
        Returns the maximum height of the target for which the items are completely below the given heightlevel.

        Parameters.
        -----------
        heightlevel: int
            The height on the target in millimeters for that defines which items are counted as unpalletized.

        Returns.
        --------
        max_target_height: int
            The maximum target height below a given height level in millimeters.
        """
        max_target_height = 0
        for item in self.getPlacedItems():
            item_z_location = max(item.getCoordinatesHeightRange())
            if item_z_location > max_target_height and item_z_location <= heightlevel:
                max_target_height = item_z_location

        return max_target_height

    def __identifyNeighbors(self, item: Cuboid, possibleneighbors: list[Cuboid]) -> None:
        """
        Identifies the neighbors of the given item and stores the neighbors of item in the object.

        This method checks
        (1) whether the item is located next to an item in the possible neighbors.
        (2) The top of a possible neighbor item has to be in the height range of given item.
        (3) If (2) is satisfied, we have to check whether the items below the possible neighbor are neighbors as well.
        (4) If (2) is not satisfied, we know that neither the possible neighbor, nor the items below are neighbors.

        Parameters.
        -----------
        item: Item3D
            The item for which the neighbors are identified.
        possibleneighbors: list (of Item3D objects)
            Items that could be neighbors of item.
        """
        EDGES_TO_COMPARE = {0: ["north", "south"], 1: ["east", "west"], 2: ["south", "north"], 3: ["west", "east"]}
        """Holds the combination of the edges that have to be compared, formatted as [edge_of_item, edge_of_possible_neighbor]"""

        identified_neighbors = {"north": [], "east": [], "south": [], "west": []}

        all_items_investigated = possibleneighbors == []

        while not all_items_investigated:
            neighbor_to_investigate = possibleneighbors.pop(0)

            for edge_item, edge_possible_neighbor in EDGES_TO_COMPARE.values():
                item_edge = item.getCoordinatesEdge(edge_item)
                possible_neighbor_edge = neighbor_to_investigate.getCoordinatesEdge(edge_possible_neighbor)

                x_intersection, y_intersection = (
                    set.intersection(item_edge["x"], possible_neighbor_edge["x"]),
                    set.intersection(item_edge["y"], possible_neighbor_edge["y"]),
                )

                if len(x_intersection) and len(y_intersection):
                    # neighbors in x-y-direction
                    # make height check
                    item_occupied_height = item.getCoordinatesHeightRange()
                    possible_neighbor_occupied_height = neighbor_to_investigate.getCoordinatesHeightRange()

                    z_intersection = set.intersection(item_occupied_height, possible_neighbor_occupied_height)
                    height_check_successful = len(z_intersection) > 0

                    if height_check_successful:
                        identified_neighbors[edge_item].append(neighbor_to_investigate)

                    # investigate items below when min height of item less than highest point of possible neighbor
                    if min(item_occupied_height) < max(possible_neighbor_occupied_height):
                        possibleneighbors += neighbor_to_investigate.getItemsBelow()
                        # remove duplicates
                        possibleneighbors = list(set(possibleneighbors))

            all_items_investigated = possibleneighbors == []

        item.storeNeighbors(identified_neighbors)

    def getCornerPointsIn3D(self, itemdimension: tuple = (0, 0, 0)) -> list:
        """
        Determines the corner points of the placed items and returns them. The corner points are calculated like described in the algorithms `2D-CORNERS` and `3D-CORNERS` in (Martello et al, 2000).

        Parameters.
        -----------
        itemdimensions: tuple
            The length, width, and height of an item for which the corner points are calculated.

        Returns.
        --------
        three_dim_corner_points: list
            The corner points for an item that has the given dimension.
        """
        placed_items = self.getPlacedItems()
        if placed_items == []:
            return [(0, 0, 0)]

        # create a list of height levels
        target_height_levels = [0] + list(set([item.flb.z + item.height for item in placed_items]))
        target_height_levels.sort()

        three_dim_corner_points = []
        prev_2d_corner_points = []

        for height_value in target_height_levels:
            # stop search if first time a placement would exceed the maximum height
            if height_value + itemdimension[2] > MAXHEIGHT:
                break

            # create a subset of placed items that are located above the height level
            I_k = [item for item in placed_items if ((item.flb.z + item.height) > height_value)]

            # search for corner points in 2D
            two_dim_corner_points = self.__get2DCorners(I_k, itemdimension[0:2])

            # check for true corner points
            for corner_point in two_dim_corner_points:
                if corner_point not in prev_2d_corner_points:
                    # create corner point in 3D
                    corner_point_3d = corner_point + (height_value,)
                    three_dim_corner_points.append(corner_point_3d)

            # update prev_2d_corner_points
            prev_2d_corner_points = two_dim_corner_points

        return three_dim_corner_points

    def __get2DCorners(self, placeditems: list[Cuboid], itemdimension: tuple) -> list:
        """
        Determines the corner points of the placed items and returns them. The corner points are calculated like described in the algorithm `2D-CORNERS` in (Martello et al, 2000).

        Parameters.
        -----------
        placeditems: list
            List of items that are placed in the 2D area.
        itemdimension: 2-tuple
            The length and width of an item for which the corner points are calculated.

        Returns.
        --------
        two_dim_corner_points: list
            The corner points for an item that has the given dimension.
        """

        def __getEndpointYthenX(item: Cuboid) -> tuple:
            """Returns the endpoint of the item as (y, x)."""
            delta_y, delta_x = item.getRepresentation().shape
            return (item.flb.y + delta_y, item.flb.x + delta_x)

        if placeditems == []:
            return [(0, 0)]

        # sort placeditems
        placeditems.sort(key=__getEndpointYthenX, reverse=True)

        # determine extreme points
        items_for_extreme_points: list[Cuboid] = []
        max_x_xalue = 0
        for item in placeditems:
            value_endpoint_x = item.flb.x + item.getRepresentation().shape[1]
            if (value_endpoint_x) > max_x_xalue:
                items_for_extreme_points.append(item)
                max_x_xalue = value_endpoint_x

        # determine coordinates of corner points
        n_extreme_points = len(items_for_extreme_points)
        two_dim_corner_points = []
        first_candidate = items_for_extreme_points.pop(0)
        previous_x = first_candidate.flb.x + first_candidate.getRepresentation().shape[1]
        previous_y = first_candidate.flb.y + first_candidate.getRepresentation().shape[0]
        two_dim_corner_points.append((0, previous_y))

        if n_extreme_points > 1:
            last_candidate = items_for_extreme_points.pop()
            last_x = last_candidate.flb.x + last_candidate.getRepresentation().shape[1]

            for candidate in items_for_extreme_points:
                candidate_x = candidate.flb.x + candidate.getRepresentation().shape[1]
                candidate_y = candidate.flb.y + candidate.getRepresentation().shape[0]

                two_dim_corner_points.append((previous_x, candidate_y))
                previous_x = candidate_x
        else:
            last_x = previous_x
        two_dim_corner_points.append((last_x, 0))

        # remove infeasible corner points
        for corner_point in two_dim_corner_points.copy():
            if (corner_point[0] + itemdimension[0] > self._size[0]) or (
                corner_point[1] + itemdimension[1] > self._size[1]
            ):
                two_dim_corner_points.remove(corner_point)

        return two_dim_corner_points
