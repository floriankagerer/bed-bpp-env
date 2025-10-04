"""
This heuristic always takes a palletizing position that *seems* to be the lowest. That means, the heuristic does not check whether an item can be placed in the selected position without "causing collisions" with any other items.

For example, if the heuristic selects the coordinates `(0, 0)` for placing an `(200, 200, 100)`-item, but the only other item on the target is a `(100, 100, 100)` item with its FLB corner in `(100,100,0)`, then the FLB corner of the first item is not in `(0,0,0)`, but in `(0,0100)`. Thus, this heuristic has its disadvantages.
"""

import numpy as np


class LowestArea:
    """
    This heuristic always takes a palletizing position that *seems* to be the lowest. That means, the heuristic does not check whether an item can be placed in the selected position without "causing collisions" with any other items.

    For example, if the heuristic selects the coordinates `(0, 0)` for placing an `(200, 200, 100)`-item, but the only other item on the target is a `(100, 100, 100)` item with its FLB corner in `(100,100,0)`, then the FLB corner of the first item is not in `(0,0,0)`, but in `(0,0100)`. Thus, this heuristic has its disadvantages.

    Attributes.
    -----------
    __Info: dict
        The additional info that is provided by the palletizing environment.
    __Observation: np.ndarray
        The stored heights of the palletizing environment.
    """

    def __init__(self) -> None:
        self.__Observation = None
        """The stored heights of the palletizing environment."""
        self.__Info = None
        """The additional info that is provided by the palletizing environment."""

    def getAction(self, observation: np.ndarray, info: dict) -> dict:
        """
        Return an action, depending on the given observation and information. This heuristic selects the first item that occurs in next items selection.

        Parameters.
        -----------
        observation: np.ndarray
            Contains the height values in each coordinate of the palletizing target in millimeters.
        info: dict
            Additional information about the palletizing environment. It must contain the keys `"allowed_area"`.

        Returns.
        --------
        action: dict
            Returns the `"x"`- and `"y"`-coordinates, and the item's `"orientation"` as ints.

        Example.
        --------
        >>> action = {
                "x": 100,
                "y": 100,
                "orientation": 0,
                "item": {'article': 'cake-00104295', 'id': 'c00104295', 'product_group': 'confectionery', 'length/mm': 590.0, 'width/mm': 200.0, 'height/mm': 210.0, 'weight/kg': 7.67, 'lc_type': 'tbd', 'sequence': 1}
            }
        """
        # set the attributes
        self.__Observation = observation
        self.__Info = info

        nextItem = self.__Info.get("next_items_selection")[0]

        # get the allowed actions
        allowedActions = self.__getAllowedActions()
        allowedActions.sort(key=self.__getHeightInCoordinate)

        selectedAction = allowedActions[0]
        action = {
            "x": int(selectedAction["coordinates"][1]),
            "y": int(selectedAction["coordinates"][0]),
            "orientation": selectedAction["orientation"],
            "item": nextItem,
        }

        return action

    def __getAllowedActions(self) -> list:
        """
        Depending on the values of the allowed area arrays, the coordinates and the corresponding orientation of an item are added to the list of allowed actions.

        Returns.
        --------
        allowedActions: list
            All actions that are allowed.
        """
        allowedActions = []
        for orientation, arrayAllowedArea in self.__Info["allowed_area"].items():
            allowedCoordinates = list(np.argwhere(arrayAllowedArea == 1))
            allowedActions += [{"coordinates": coord, "orientation": orientation} for coord in allowedCoordinates]

        return allowedActions

    def __getHeightInCoordinate(self, action: dict) -> int:
        """
        Returns the height in the given coordinates that were defined by the action.

        Parameters.
        -----------
        action: dict
            Contains the `"coordinates"` and the `"orientation"` of an item.

        Returns.
        --------
        height: int
            The height in the given coordinate in millimeters.
        """
        coordinate = action["coordinates"]
        return self.__Observation[coordinate[0], coordinate[1]]
