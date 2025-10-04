"""
Similar to `PalletizingEnvironment`, but with little changes for the tasks with preview and selection.
"""

import configparser
from typing import Tuple
import pathlib
import environment
import evaluation
import json
import gymnasium as gym
from gymnasium.spaces import Discrete, Dict, Box
import logging
import numpy as np
import copy


logger = logging.getLogger(__name__)

SIZE_ROLLCONTAINER = environment.SIZE_ROLLCONTAINER
"""The base area of the target "rollcontainer" in millimeters."""
SIZE_EURO_PALLET = environment.SIZE_EURO_PALLET
"""The base area of the target "euro-pallet" in millimeters."""

MAXHEIGHT_OBSERVATION_SPACE = environment.MAXHEIGHT_OBSERVATION_SPACE
"""The maximum height of the observation space in millimeters."""

import utils

RENDER = utils.PARSEDARGUMENTS.get("visualize", False)

conf = configparser.ConfigParser()
conf.read(utils.configuration.USEDCONFIGURATIONFILE)


class SimPalEnv(gym.Env):
    """
    Similar to `PalletizingEnvironment`, but with little changes for the tasks with preview and selection.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self) -> None:
        self.__Size = SIZE_EURO_PALLET
        """The palletizing target's size of the base area in x- and y-direction given in millimeters."""
        self.__N_ORIENTATION = 2
        """The amount of different orientations that are allowed during palletization."""

        self.action_space = Dict(
            {
                "x": Discrete(self.__Size[0]),
                "y": Discrete(self.__Size[1]),
                "orientation": Discrete(self.__N_ORIENTATION),
            }
        )
        """The action space consists of the simple action spaces for x-, y-coordinate and the orientation of the item."""

        self.observation_space = Box(
            low=0, high=MAXHEIGHT_OBSERVATION_SPACE, shape=(self.__Size[1], self.__Size[0]), dtype=int
        )
        """The observation space describes the heights in each coordinate on the palletizing target."""

        self.__TargetSpace = environment.Space3D(self.__Size)
        """Represents the 3D space where the palletization takes place."""

        self.__Actions = []
        """A list that stores all actions done in the order of their palletizing point in time."""

        self.__PalletizedVolume = 0.0
        """A float that stores the palletized volume of all items in cm^3."""

        self.__Orders = {}
        """The orders that are given whenever the method `reset` is called with a non-empty parameter `data_for_episodes`. The format is identical to the format of the benchmark data."""
        self.__CurrentOrder = {}
        """This dictionary has the keys `"key"`, `"order"`, and `"seq"`, whose values store the key of the order as given in the order data, the current order itself, and the number in the sequence of all orders, respectively."""
        self.__OrderSequence = []  # list of the keys of the given order data
        """This list contains all keys in the order data in the same order as it is given."""
        self.__ItemSequenceCounter = None
        """This integer stores the position within an item sequence of the current order."""

        self.__NItemPreview = int(conf.get("environment", "preview"))
        """The amount of preview items."""
        self.__NItemSelection = int(conf.get("environment", "selection"))
        """The amount of items to select from, i.e., to select for the next step."""

        self.__ItemsSelection = []
        """The items to select from for the next palletizing step."""
        self.__ItemsPreview = []
        """The preview items."""

        self.__KPIs = evaluation.KPIs()
        """Holds the values of the KPIs for each order."""

        self.__MPScoreEstimation = False
        """Needed for the update item preview """

    def step(self, action: dict) -> Tuple[np.ndarray, float, bool, dict]:
        """
        In the step function we have to palletize the given item at the given position. Translated to this implementation that means that we have to
        (a) calculate the z-coordinate of the placement for the given action (x-,y-coordinate and orientation of item),
        (b) append the item to the palletized items,
        (c) update the height map of the palletizing target,
        (d) obtain the allowed positions for the upcoming item,
        (e) obtain the reward of the step, and
        (f) obtain the additional information.

        Parameters.
        -----------
            action: dict
                The action contains the `"x"` and `"y"` coordinate of the placement, the item and its `"orientation"`.

        Returns.
        --------
            stepReturns: tuple
                The step method returns the new observation (`object`), the reward (`float`), whether the episode has ended (`bool`) and additional information (`dict`).

        Examples.
        ---------
        >>> action = {
                "x": 100, # int
                "y": 100, # int
                "orientation": 0, # int
                "item": {'article': 'cake-00104295', 'id': 'c00104295', 'product_group': 'confectionery', 'length/mm': 590, 'width/mm': 200, 'height/mm': 210, 'weight/kg': 7.67, 'sequence': 1}
            }
        """
        info = {}

        # get the variables that are needed here
        sVars = self.__getStepVariables(action)
        itemForAction = action["item"]

        # define the item
        item = environment.Item3D(sVars["item"])
        item.setOrientation(sVars["orientation"])

        # create a np.ndarray that has the same shape as the target, its elements are 1 if the item is located in this region and 0 otherwise
        itemOnTarget = np.zeros((self.__Size[1], self.__Size[0]), dtype=int)
        itemDeltaY, itemDeltaX = item.getRepresentation().shape
        startX, startY = sVars["xCoord"], sVars["yCoord"]
        try:
            itemOnTarget[startY : startY + itemDeltaY, startX : startX + itemDeltaX] = np.ones(
                item.getRepresentation().shape, dtype=int
            )
        except:
            # have to crop item like in `environment.Space3D.addItem`
            logger.warning(f"cropped item")
            croppedShape = (
                min(itemOnTarget.shape[0], startY + itemDeltaY) - startY,
                min(itemOnTarget.shape[1], startX + itemDeltaX) - startX,
            )
            itemOnTarget[startY : startY + croppedShape[0], startX : startX + croppedShape[1]] = np.ones(
                croppedShape, dtype=int
            )

        # obtaiin the FLB height for the item in the selected (x, y)-coordinate
        maxHeightInTargetArea = int(np.amax(np.multiply(self.__TargetSpace.getHeights(), itemOnTarget)))

        # define the action in the needed format
        actionExt = {
            "item": sVars["item"],
            "flb_coordinates": [sVars["xCoord"], sVars["yCoord"], maxHeightInTargetArea],
            "orientation": sVars["orientation"],
        }
        self.__Actions.append(actionExt)
        info.update({"action_for_vis": actionExt})
        logger.debug(f"step() -> extended action: {actionExt}")

        # add the item to the palletizing target
        self.__TargetSpace.addItem(item, actionExt["orientation"], actionExt["flb_coordinates"])
        info.update({"support_area/%": item.getPercentageDirectSupportSurface()})

        # prepare for next call of step
        additionalInfo = self.__prepareForNextStep(itemForAction)
        done = additionalInfo.pop("done")
        info.update(additionalInfo)

        # update the attributes
        self.__PalletizedVolume += (sVars["deltaX"] * sVars["deltaY"] * sVars["itemHeight"]) / 1000.0
        self.__KPIs.update()

        reward = self.__getReward(done)
        info = self.__getInfo("step", info)

        stepReturns = self.__TargetSpace.getHeights(), reward, done, info
        return stepReturns

    def reset(self, data_for_episodes: dict = {}) -> Tuple[np.ndarray, dict]:
        """
        This method is responsible for
        (a) the change of the orders, e.g., from "00100001" -> "00100002",
        (b) the reset of the stored attributes and heights of the virtual palletizing target,
        (c) obtaining the inital observation and information about the environment,
        (d) resetting the target's size of the base area, depending on the goal that is defined in the given data for the episodes, and
        (e) loading the order data that shoud be considered.

        Parameters.
        -----------
        data_for_epsidoes: dict (default = {})
            The data for the episodes in the format of the benchmark data.

        Returns.
        --------
        observation: np.array
            The stored heights of the environment.
        info: dict
            A dictionary that contains additional information that might be useful for the machine learning agent.
        """
        # # # # # Change the Order that is considered # # # # #
        done = False
        # change the current order
        if self.__CurrentOrder == {} or not (data_for_episodes == {}):
            self.__Orders = data_for_episodes
            self.__OrderSequence = list(self.__Orders.keys())
            self.__CurrentOrder["seq"] = 0
            orderKey = self.__OrderSequence[self.__CurrentOrder["seq"]]
            self.__CurrentOrder["key"] = orderKey
            self.__CurrentOrder["order"] = self.__Orders[orderKey]

            self.__ItemSequenceCounter = 1

        elif self.__CurrentOrder["seq"] + 1 >= len(self.__OrderSequence):
            # reached the last order in the data
            done = True
            self.__CurrentOrder["seq"] += 1
        else:
            self.__CurrentOrder["seq"] += 1
            orderKey = self.__OrderSequence[self.__CurrentOrder["seq"]]
            self.__CurrentOrder["key"] = orderKey
            self.__CurrentOrder["order"] = self.__Orders[orderKey]
            self.__ItemSequenceCounter = 1

        if not (done):
            logger.debug(f"{self.__CurrentOrder}")

        # # # # # Reset the Attributes # # # # #
        # change the size related to the palletizing target and the action space
        palletizingTarget = self.__CurrentOrder["order"]["properties"]["target"]
        if palletizingTarget == "rollcontainer":
            self.__Size = SIZE_ROLLCONTAINER
        elif palletizingTarget == "euro-pallet":
            self.__Size = SIZE_EURO_PALLET
        else:
            # size is given as `"x,y,z"`
            sizes = palletizingTarget.split(",")
            self.__Size = tuple([int(sizes[0]), int(sizes[1])])

        self.action_space = Dict(
            {
                "x": Discrete(self.__Size[0]),
                "y": Discrete(self.__Size[1]),
                "orientation": Discrete(self.__N_ORIENTATION),
            }
        )

        self.__TargetSpace.reset(self.__Size)
        self.__Actions = []
        self.__PalletizedVolume = 0.0
        self.__KPIs.reset(self.__TargetSpace, self.__CurrentOrder)

        self.__ItemsSelection = []
        self.__ItemsPreview = []
        if not (done):
            # only update items if we do not
            self.__updateItemsSelection()
            self.__updateItemsPreview()

        # # # # # Obtain the Observation and Info # # # # #
        observation = self.__TargetSpace.getHeights()
        info = self.__getInfo("reset")

        return observation, info

    def render(self, mode="human") -> None:
        pass

    def close(self) -> None:
        pass

    def __getReward(self, done: bool) -> float:
        """
        You can define your reward here.
        """
        if done:
            reward = 1.0
        else:
            reward = 0.0
        return reward

    def __getInfo(self, calledby: str = "step", additionalinfo: dict = {}) -> dict:
        """Get the info dictionary after reset or step"""
        info = additionalinfo

        if calledby == "step":
            info.update(
                {
                    "all_orders_considered": None,
                    "item_volume_on_target/cm^3": self.__PalletizedVolume,
                    "n_items_in_order": len(self.__CurrentOrder["order"]["item_sequence"]),
                }
            )

        elif calledby == "reset":
            # obtain whether all orders are considered
            done = self.__CurrentOrder["seq"] >= len(
                self.__OrderSequence
            )  # do not need +1 because the counter is already increased

            if not (done):
                nextItems = self.__obtainNextItems()
                item = nextItems["selection"][0]

                cornerPoints = self.__determineCornerPoints(nextItems["selection"])

                info.update(
                    {
                        "all_orders_considered": done,
                        "order_id": self.__CurrentOrder["key"],
                        "next_items_selection": nextItems["selection"],
                        "next_items_preview": nextItems["preview"],
                        "corner_points": cornerPoints,
                    }
                )

            else:
                # all orders considered
                info.update(
                    {
                        "all_orders_considered": done,
                        "order_id": None,
                        "next_items_selection": [],
                        "next_items_preview": [],
                        "corner_points": {},
                    }
                )

        return info

    def __getStepVariables(self, action: dict) -> dict:
        """This method creates the variables that are needed in the `step` method, depending on the given action."""
        orientation = action["orientation"]
        xCoord, yCoord = int(action["x"]), int(action["y"])

        item = action["item"]
        itemLength, itemWidth, itemHeight = int(item["length/mm"]), int(item["width/mm"]), int(item["height/mm"])

        if orientation == 0:
            deltaX, deltaY = itemLength, itemWidth
        elif orientation == 1:
            deltaX, deltaY = itemWidth, itemLength

        stepVar = {
            "xCoord": xCoord,
            "yCoord": yCoord,
            "deltaX": deltaX,
            "deltaY": deltaY,
            "itemHeight": itemHeight,
            "orientation": orientation,
            "item": item,
        }

        return stepVar

    def __prepareForNextStep(self, placeditem: dict) -> dict:
        """
        This method prepares the environment for the next call of the `step` method. Hence, the __ItemSequenceCounter is increased and the next palletizing items and their allowed positions on the target are calculated, unless the current episode has not finished (after the currently called `step`).

        Returns.
        --------
            info: dict
                Information that is returned by the `step` method.
        """
        info = {}

        self.__ItemSequenceCounter += 1
        if self.__ItemSequenceCounter > len(self.__CurrentOrder["order"]["item_sequence"]):
            done = True  # episode finished
            info.update({"next_items_selection": [], "next_items_preview": []})
        else:
            done = False
            self.__updateItemsSelection(placeditem)
            self.__updateItemsPreview()
            nextItems = self.__obtainNextItems()

            # get the corner points for the items that can be selected
            cornerPoints = self.__determineCornerPoints(nextItems["selection"])

            info.update(
                {  # "allowed_area": allowedArea,
                    "next_items_selection": nextItems["selection"],
                    "next_items_preview": nextItems["preview"],
                    "corner_points": cornerPoints,
                }
            )

        info.update({"done": done})

        return info

    def __obtainNextItems(self) -> dict:
        """
        Returns a dictionary that contains the next items in the item sequence of order that is currently considered. Depending on the task, i.e., on the specified values for the preview `k` and the selection `s`, the lenght of the returned item list differs.

        As example, if the task `"O3DBP-k-s"` is loaded, then the length of the list with the selection items is `s`, and the list of the preview items is `k-s`. In general, the preview list is not empty, if and only if `k > s`.

        If less items are left in the item sequence as the values of `k` and `s` would request, instead of the item's properties an empty dictionary is appended.

        Returns.
        --------
        nextItems: dict
            Contains the next items in the item sequence.

        Examples.
        ---------
        >>> self.__obtainNextItems() # with k=s=1
        {
            "selection": [{"article": "article_1", "id": "id_1", "product_group": "pg_1", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 1}],
            "preview": []
        }
        >>> self.__obtainNextItems() # with k=3; s=1
        {
            "selection": [{"article": "article_1", "id": "id_1", "product_group": "pg_1", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 1}],
            "preview": [{"article": "article_2", "id": "id_2", "product_group": "pg_2", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 2}, {"article": "article_3", "id": "id_3", "product_group": "pg_3", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 3}]
        }

        """
        nextItems = {"selection": self.__ItemsSelection, "preview": self.__ItemsPreview}
        return nextItems

    def __determineCornerPoints(self, possibleitems: list) -> dict:
        """
        Determines the corner points for all items that are given.

        Parameters.
        -----------
        possibleitems: list
            Contains the item dictionary of the items that could be selected for palletization.

        Returns.
        --------
        cornerPoints: list
            The corner points for an item that is specified by its dimension.
        """
        cornerPoints = {}
        for item in possibleitems:
            itemArticle = item.get("article", None)
            if not (itemArticle is None):
                cornerPoints[itemArticle] = {}
                for orientation in range(self.__N_ORIENTATION):
                    if orientation == 0:
                        length, width, height = item.get("length/mm"), item.get("width/mm"), item.get("height/mm")
                    elif orientation == 1:
                        width, length, height = item.get("length/mm"), item.get("width/mm"), item.get("height/mm")

                    cornerPoints[itemArticle][orientation] = self.__TargetSpace.getCornerPointsIn3D(
                        (length, width, height)
                    )

        return cornerPoints

    def getNPlacedItems(self) -> int:
        """Returns the amount of placed items in the environment."""
        return len(self.__Actions)

    def __updateItemsSelection(self, itemdict: dict = {}) -> None:
        """
        This method updates the items that can be selected.

        Parameters.
        -----------
        itemdict: dict
            The properties of the item that was palletized in the last `env.step` call.

        Important.
        ----------
        Call this method before `self.__updateItemsPreview`.
        """
        if (self.__ItemSequenceCounter == 1) or (len(self.__ItemsPreview) == 0):
            if not (self.__ItemSequenceCounter == 1):
                # not first call -> remove itemdict from selection
                self.__ItemsSelection.remove(itemdict)
            # first call in env.reset in an episode
            for s in range(self.__NItemSelection):
                itemKey = str(self.__ItemSequenceCounter + s)
                if itemKey in self.__CurrentOrder["order"]["item_sequence"].keys():
                    self.__ItemsSelection.append(
                        self.__CurrentOrder["order"]["item_sequence"][str(self.__ItemSequenceCounter + s)]
                    )
                else:
                    self.__ItemsSelection.append({})
        else:
            # call in env.step
            self.__ItemsSelection.remove(itemdict)
            self.__ItemsSelection.append(self.__ItemsPreview.pop(0))

    def __updateItemsPreview(self) -> None:
        """
        This method updates the items that are known in advance, but cannot be selected.

        Different to PalletizingEnvironment.py

        Important.
        ----------
        Call this method after `self.__updateItemsSelection`.
        """
        if self.__MPScoreEstimation:
            for k in range(self.__NItemSelection, self.__NItemPreview):
                nPurePrevItems = self.__NItemPreview - self.__NItemSelection
                if not (len(self.__ItemsPreview) >= nPurePrevItems):
                    self.__ItemsPreview.append({})

        else:
            for k in range(self.__NItemSelection, self.__NItemPreview):
                itemCounter = self.__ItemSequenceCounter + k
                itemKey = str(itemCounter)
                if itemKey in self.__CurrentOrder["order"]["item_sequence"].keys():
                    prevItem = self.__CurrentOrder["order"]["item_sequence"][itemKey]
                    if not (prevItem in self.__ItemsPreview):
                        self.__ItemsPreview.append(prevItem)
                else:
                    nPurePrevItems = self.__NItemPreview - self.__NItemSelection
                    if not (len(self.__ItemsPreview) >= nPurePrevItems):
                        self.__ItemsPreview.append({})

    def setItems(self, preview: list, selection: list) -> None:
        """Sets the preview and selection items."""
        self.__ItemsSelection = copy.deepcopy(selection)
        self.__ItemsPreview = copy.deepcopy(preview)

        self.__MPScoreEstimation = True

    def remStoredOrder(self) -> None:
        """
        Deletes the stored benchmark data order.

        => Reduce time copy.deepcopy needs
        """
        del self.__Orders
