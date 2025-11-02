"""
The module `PalletizingEnvironment` contains a class that is based on OpenAI's `gym` API that can easily be used for palletizing simulations.

Depending on the task, e.g., `"O3DBP-k-s"`, the dictionary that contains additional information after a `reset` or `step` call, holds a different amount of next items. The `s` items an agent can choose to place next are stored in this dictionary with the key `"next_items_selection"`. In order to know which `k-s` items come after the selection, get the list that is stored with the key `"next_items_preview"` in the info dictionary.
"""

import configparser
import json
import logging
import pathlib
import platform
from typing import Optional

import cv2
import gymnasium as gym
import numpy as np
import PIL
from gymnasium.spaces import Box, Dict, Discrete
from PIL import Image, ImageDraw, ImageFont

from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.order import Order
from bed_bpp_env.data_model.position_3d import Position3D
from bed_bpp_env.environment import MAXHEIGHT_OBSERVATION_SPACE, SIZE_EURO_PALLET, SIZE_ROLLCONTAINER
from bed_bpp_env.environment.cuboid import Cuboid
from bed_bpp_env.environment.lc import LC
from bed_bpp_env.environment.space_3d import Space3D
from bed_bpp_env.evaluation.kpis import KPIs
from bed_bpp_env.utils import OUTPUTDIRECTORY, PARSEDARGUMENTS
from bed_bpp_env.utils.configuration import USEDCONFIGURATIONFILE
from bed_bpp_env.visualization.palletizing_environment_visualization import PalletizingEnvironmentVisualization

RENDER = PARSEDARGUMENTS.get("visualize", False)

logger = logging.getLogger(__name__)

conf = configparser.ConfigParser()
conf.read(USEDCONFIGURATIONFILE)


class PalletizingEnvironment(gym.Env):
    """
    The PalletizingEnvironment is a class that can be used for palletizing simulation. Since it is based on OpenAI `gym`, the known API can be used. The methods can be interpreted as
    (a) `step`: palletize an item in which the given action defines the x- and y-coordinates of the item and its orientation. The z-coordinate is calculated within this method.
    (b) `reset`: start the palletization of items, i.e., the first item of an order is considered and the palletizing target is empty.
    (c) `render`: visualize the current status of the palletization.
    (d) `close`: stop the palletization.

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Note

    We must save the heights in mm steps and provide the allowed areas in mm steps, since otherwise information gets lost and due to rounding errors we do not palletize them in the "best" positions.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self) -> None:
        self._size = SIZE_EURO_PALLET
        """The palletizing target's size of the base area in x- and y-direction given in millimeters."""
        self._n_orientations = 2
        """The amount of different orientations that are allowed during palletization."""

        self._size_multiplicator = 1
        """TBD needed for rescalewrapper and isItemSelectable"""

        self.action_space = Dict(
            {
                "x": Discrete(self._size[0]),
                "y": Discrete(self._size[1]),
                "orientation": Discrete(self._n_orientations),
            }
        )
        """The action space consists of the simple action spaces for x-, y-coordinate and the orientation of the item."""

        self.observation_space = Box(
            low=0, high=MAXHEIGHT_OBSERVATION_SPACE, shape=(self._size[1], self._size[0]), dtype=int
        )
        """The observation space describes the heights in each coordinate on the palletizing target."""

        self._target_space = Space3D(self._size)
        """Represents the 3D space where the palletization takes place."""

        self._actions = []
        """A list that stores all actions done in the order of their palletizing point in time."""

        self._palletized_volume = 0.0
        """A float that stores the palletized volume of all items in cm^3."""

        self._orders = {}
        """The orders that are given whenever the method `reset` is called with a non-empty parameter `data_for_episodes`. The format is identical to the format of the benchmark data."""
        self._current_order: Optional[Order] = None
        """This dictionary has the keys `"key"`, `"order"`, and `"seq"`, whose values store the key of the order as given in the order data, the current order itself, and the number in the sequence of all orders, respectively."""
        self._order_sequence = []  # list of the keys of the given order data
        """This list contains all keys in the order data in the same order as it is given."""
        self._item_sequence_counter = None
        """This integer stores the position within an item sequence of the current order."""

        self._visualization = None
        """This object creates a visualization of the current palletizing status."""

        self._packing_plans = {}
        """The created packing plans of the solver/agent."""

        self._n_item_preview = int(conf.get("environment", "preview"))
        """The amount of preview items."""
        self._n_item_selection = int(conf.get("environment", "selection"))
        """The amount of items to select from, i.e., to select for the next step."""

        self._items_selection = []
        """The items to select from for the next palletizing step."""
        self._items_preview = []
        """The preview items."""

        self._kpis = KPIs()
        """Holds the values of the KPIs for each order."""

    def step(self, action: dict) -> tuple[np.ndarray, float, bool, dict]:
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
        step_vars = self._get_step_variables(action)
        item_for_action = action["item"]
        if not (self.__isItemSelectable(item_for_action)):
            raise ValueError(f"item {item_for_action} must not be selected.")

        # define the item
        item = Cuboid(item_for_action)
        item.set_orientation(step_vars["orientation"])

        # create a np.ndarray that has the same shape as the target, its elements are 1 if the item is located in this region and 0 otherwise
        item_on_target = np.zeros((self._size[1], self._size[0]), dtype=int)
        item_delta_y, item_delta_x = item.array_representation.shape
        start_x, start_y = step_vars["xCoord"], step_vars["yCoord"]
        try:
            item_on_target[start_y : start_y + item_delta_y, start_x : start_x + item_delta_x] = np.ones(
                item.array_representation.shape, dtype=int
            )
        except Exception:
            # have to crop item like in `environment.Space3D.addItem`
            logger.warning("cropped item")
            cropped_shape = (
                min(item_on_target.shape[0], start_y + item_delta_y) - start_y,
                min(item_on_target.shape[1], start_x + item_delta_x) - start_x,
            )
            item_on_target[start_y : start_y + cropped_shape[0], start_x : start_x + cropped_shape[1]] = np.ones(
                cropped_shape, dtype=int
            )

        # obtaiin the FLB height for the item in the selected (x, y)-coordinate
        max_height_in_target_area = int(np.amax(np.multiply(self._target_space.getHeights(), item_on_target)))

        # define the action in the needed format
        action_extended = {
            "item": item_for_action,
            "flb_coordinates": [step_vars["xCoord"], step_vars["yCoord"], max_height_in_target_area],
            "orientation": step_vars["orientation"],
        }
        self._actions.append(action_extended)
        info.update({"action_for_vis": action_extended})
        logger.info(f"step() -> extended action: {action_extended}")

        # add the item to the palletizing target
        self._target_space.addItem(item, action_extended["orientation"], action_extended["flb_coordinates"])
        info.update({"support_area/%": item.percentage_direct_support_surface})

        # prepare for next call of step
        additional_info = self.__prepareForNextStep(item_for_action)
        done = additional_info.pop("done")
        info.update(additional_info)

        # update the attributes
        self.__updatePalletVisualization(action_extended)
        self._palletized_volume += (step_vars["deltaX"] * step_vars["deltaY"] * step_vars["itemHeight"]) / 1000.0
        self._kpis.update()

        reward = self.__getReward(done)
        info = self.__getInfo("step", info, done)

        step_returns = self._target_space.getHeights(), reward, done, info
        return step_returns

    def reset(self, order_sequence: Optional[list[Order]] = None) -> tuple[np.ndarray, dict]:
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
        self.__savePackingPlan()
        # # # # # Change the Order that is considered # # # # #
        done = False
        # change the current order
        if self._current_order is None or order_sequence is not None:
            self._orders = order_sequence.copy()
            self._order_sequence = [order.id for order in self._orders]
            self._current_order = self._orders[0]

        elif self._current_order.id == self._order_sequence[-1]:
            # reached the last order in the data
            done = True

        else:
            current_order_id = self._current_order.id
            next_order_index = self._order_sequence.index(current_order_id) + 1
            self._current_order = self._orders[next_order_index]

        if not done:
            logger.info(f"CURRENT ORDER:{self._current_order.id}\n\n\n")

        # # # # # Reset the Attributes # # # # #
        self._item_sequence_counter = 0
        # change the size related to the palletizing target and the action space
        palletizing_target = self._current_order.properties.target
        if palletizing_target == "rollcontainer":
            self._size = SIZE_ROLLCONTAINER
        elif palletizing_target == "euro-pallet":
            self._size = SIZE_EURO_PALLET
        else:
            # size is given as `"x,y,z"`
            sizes = palletizing_target.split(",")
            self._size = (int(sizes[0]), int(sizes[1]))

        self.action_space = Dict(
            {
                "x": Discrete(self._size[0]),
                "y": Discrete(self._size[1]),
                "orientation": Discrete(self._n_orientations),
            }
        )

        del self._visualization
        self._visualization = PalletizingEnvironmentVisualization(
            visID=self._current_order.id, target=palletizing_target
        )

        self._target_space.reset(self._size)
        self._actions = []
        self._palletized_volume = 0.0
        self._kpis.reset(self._target_space, self._current_order)

        self._items_selection = []
        self._items_preview = []
        if not done:
            # only update items if we do not
            self.__updateItemsSelection()
            self.__updateItemsPreview()

        # # # # # Obtain the Observation and Info # # # # #
        observation = self._target_space.getHeights()
        info = self.__getInfo("reset", done=done)

        return observation, info

    def render(self, mode="human") -> None:
        """
        Renders the environment.

        Note.
        -----
        If you want to save the displayed render image, you have to uncomment two lines below in this method.
        """
        if not (RENDER):
            return None

        DISPLAYTIME = 100  # ms

        render_image = Image.new("RGB", (1800, 900), color=(255, 255, 255))
        test_status = Image.open(self._visualization.getFilenameOfImage())
        test_status = test_status.resize((800, 800))
        render_image.paste(test_status, (0, 0))

        draw = ImageDraw.Draw(render_image)
        if self._actions == []:
            pass
        else:
            # find path for font
            used_platform = platform.platform()
            if "macOS" in used_platform:
                path_to_font = "~/Library/Fonts/Arial Unicode.ttf"
            elif "Linux" in used_platform:
                path_to_font = "/usr/share/fonts/opentype/cabin/Cabin-Regular.otf"
            else:
                # windows is currently not implemented
                pass

            font_header = ImageFont.truetype(path_to_font, size=30)
            font_txt = ImageFont.truetype(path_to_font, size=20)

            action = self._actions[-1]
            item: Item = action["item"]
            txt_item = item.repr_key_value_pair()

            draw.text((700, 5), "Item", font=font_header, fill="black", align="left")
            draw.text((700, 40), txt_item, font=font_txt, fill="black", align="left")

            coordinate_from_action = action["flb_coordinates"]
            draw.text((1000, 5), "FLB Coordinates", font=font_header, fill="black", align="left")
            draw.text((1000, 40), str(coordinate_from_action), font=font_txt, fill="black", align="left")

            orientation = action["orientation"]
            draw.text((1000, 85), "Orientation", font=font_header, fill="black", align="left")
            draw.text((1000, 120), str(orientation), font=font_txt, fill="black", align="left")

            draw.text((1300, 5), "KPIs", font=font_header, fill="black", align="left")
            kpis = self._kpis.getPrettyStr()
            draw.text((1300, 40), kpis, font=font_txt, fill="black", align="left")

            pallet_heights = self._target_space.getHeights()
            draw.text(
                (700, 300),
                f"State of Env (h {MAXHEIGHT_OBSERVATION_SPACE}mm => white)",
                font=font_header,
                fill="black",
                align="left",
            )
            draw.text((700, 335), f"Size = {pallet_heights.shape}", font=font_txt, fill="black", align="left")

            test_state = Image.fromarray((pallet_heights * 255 / 2500).astype(float))  # np.uint8))
            h_flipped_state = test_state.transpose(PIL.Image.FLIP_TOP_BOTTOM)
            h_flipped_state = h_flipped_state.resize((h_flipped_state.size[0] // 2, h_flipped_state.size[1] // 2))
            render_image.paste(h_flipped_state, (700, 365))

        # # uncomment the lines below if you want to save the render image
        # fname = f"vis_{self._current_order['key']}_{self._item_sequence_counter}.png" # "render_image.png"
        # targetpathForRenderImage = pathlib.Path.joinpath(utils.OUTPUTDIRECTORY, fname)
        # render_image.save(targetpathForRenderImage)

        windowname = "BED-BPP Environment | Render Image"
        cv2.namedWindow(windowname)  # , cv2.WINDOW_NORMAL)
        cv2.moveWindow(windowname, 0, 0)
        # cv2.setWindowProperty(windowname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        img1 = cv2.cvtColor(np.array(render_image), cv2.COLOR_RGB2BGR)
        cv2.imshow(windowname, img1)
        cv2.waitKey(DISPLAYTIME)

    def close(self) -> None:
        self.__savePackingPlan(True)

    # utils

    def __isItemSelectable(self, item: Item) -> bool:
        """
        This method checks whether the item that is given in an action is selectable in the current situation.

        Parameters.
        -----------


        Returns.
        --------
        selectable: bool
            Indicates whether the item is selectable.
        """
        selectable = False

        if self._size_multiplicator != 1:
            # adapt the item size whenever the RescaleWrapper is used
            item.length_mm *= self._size_multiplicator[0]
            item.width_mm *= self._size_multiplicator[1]

        if item in self._items_selection:
            selectable = True

        return selectable

    def __savePackingPlan(self, tofile: bool = False) -> None:
        if self._current_order is None:
            # do nothing
            pass
        else:
            order_key = self._current_order.id
            if order_key not in self._packing_plans.keys():
                # serialize items
                actions_with_serialized_items = []
                for action in self._actions:
                    item: Item = action.get("item")
                    serializable_action = action
                    serializable_action["item"] = item.to_dict()
                    actions_with_serialized_items.append(serializable_action)
                self._packing_plans[order_key] = actions_with_serialized_items

                packing_plan = {order_key: self._actions}
                logger.info(f"PackingPlan = {packing_plan}")

        if True:  # tofile:
            packing_plans_file = "packing_plans.json"
            output_file = pathlib.Path.joinpath(OUTPUTDIRECTORY, packing_plans_file)
            with open(output_file, "w") as PPFile:
                json.dump(self._packing_plans, PPFile)

    def __getReward(self, done: bool) -> float:
        """
        You can define your reward here.
        """
        if done:
            reward = 1.0
        else:
            reward = 0.0
        return reward

    def __getInfo(self, calledby: str = "step", additionalinfo: Optional[dict] = None, done: bool = False) -> dict:
        """Get the info dictionary after reset or step."""
        if additionalinfo is None:
            info = {}
        else:
            info = additionalinfo

        if calledby == "step":
            info.update(
                {
                    "all_orders_considered": None,
                    "item_volume_on_target/cm^3": self._palletized_volume,
                    "n_items_in_order": len(self._current_order.item_sequence),
                }
            )

        elif calledby == "reset":
            # if done is True, then all orders are considered
            if not done:
                # obtain np.array with allowed area
                next_items = self.__obtainNextItems()
                item = next_items["selection"][0]
                allowed_area = self._obtain_allowed_areas(item)

                corner_points = self.__determineCornerPoints(next_items["selection"])

                info.update(
                    {
                        "all_orders_considered": done,
                        "allowed_area": allowed_area,
                        "order_id": self._current_order.id,
                        "palletizing_target": self._current_order.properties.target,
                        "next_items_selection": next_items["selection"],
                        "next_items_preview": next_items["preview"],
                        "n_items_in_order": len(self._current_order.item_sequence),
                        "corner_points": corner_points,
                    }
                )

            else:
                # all orders considered
                info.update(
                    {
                        "all_orders_considered": done,
                        "allowed_area": {},
                        "order_id": None,
                        "palletizing_target": None,
                        "next_items_selection": [],
                        "next_items_preview": [],
                        "n_items_in_order": None,
                        "corner_points": {},
                    }
                )

        return info

    def _get_step_variables(self, action: dict) -> dict:
        """This method creates the variables that are needed in the `step` method, depending on the given action."""
        orientation = action["orientation"]
        x_coord, y_coord = int(action["x"]), int(action["y"])

        item: Item = action["item"]

        if orientation == 0:
            delta_x, delta_y = item.length_mm, item.width_mm
        elif orientation == 1:
            delta_x, delta_y = item.width_mm, item.length_mm

        step_var = {
            "xCoord": x_coord,
            "yCoord": y_coord,
            "deltaX": delta_x,
            "deltaY": delta_y,
            "itemHeight": item.height_mm,
            "orientation": orientation,
        }

        return step_var

    def _obtain_allowed_areas(self, item: Item) -> dict:
        """
        This method returns a dictionary that contains np.arrays, which define in which coordinates the given item can be placed.
        Returns.
        --------
        allowed_area: dict
            A dictionary whose keys define the orientation and the values define the possible coordinates of an item placement.

        Example.
        --------
        >>> allowed_area = {
                0: np.array,
                1: np.array,
                <orientation>: np.array # element == 1: allowed; element == 0: not allowed
            }
        """
        allowed_area = {}
        # if item is None:
        #     return {}  # {0: np.zeros((self._size), dtype=int), 1: np.zeros((self._size), dtype=int)}

        # create the arrays such that the item is completely inside the palletizing target
        item_length, item_width = int(item.length_mm), int(item.width_mm)
        for orientation in range(self._n_orientations):
            if orientation == 0:
                delta_x, delta_y = item_length, item_width
            elif orientation == 1:
                delta_x, delta_y = item_width, item_length

            if (self._size[1] >= delta_y) and (self._size[0] >= delta_x):
                # check whether the items can be placed in the target
                allowed_coordinates = np.zeros((self._size[1], self._size[0]), dtype=int)
                allowed_coordinates[0 : self._size[1] - delta_y, 0 : self._size[0] - delta_x] = np.ones(
                    (self._size[1] - delta_y, self._size[0] - delta_x)
                )
                allowed_area[orientation] = allowed_coordinates

        return allowed_area

    def __prepareForNextStep(self, placeditem: Item) -> dict:
        """
        This method prepares the environment for the next call of the `step` method. Hence, the _item_sequence_counter is increased and the next palletizing items and their allowed positions on the target are calculated, unless the current episode has not finished (after the currently called `step`).

        Returns.
        --------
        info: dict
            Information that is returned by the `step` method.
        """
        info = {}

        self._item_sequence_counter += 1
        if self._item_sequence_counter >= len(self._current_order.item_sequence):
            done = True  # episode finished
            info.update(
                {
                    "allowed_area": {0: np.zeros((self._size), dtype=int), 1: np.zeros((self._size), dtype=int)},
                    "next_items_selection": [],
                    "next_items_preview": [],
                }
            )
        else:
            done = False
            self.__updateItemsSelection(placeditem)
            self.__updateItemsPreview()
            next_items = self.__obtainNextItems()
            item = next_items["selection"][0]
            allowed_area = self._obtain_allowed_areas(item)

            # get the corner points for the items that can be selected
            corner_points = self.__determineCornerPoints(next_items["selection"])

            info.update(
                {
                    "allowed_area": allowed_area,
                    "next_items_selection": next_items["selection"],
                    "next_items_preview": next_items["preview"],
                    "corner_points": corner_points,
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
        next_items: dict
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
        next_items = {"selection": self._items_selection, "preview": self._items_preview}
        return next_items

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
        if (self._item_sequence_counter == 0) or (len(self._items_preview) == 0):
            if self._item_sequence_counter != 0:
                # not first call -> remove itemdict from selection
                self._items_selection.remove(itemdict)
            # first call in env.reset in an episode
            for s in range(self._n_item_selection):
                item_index = self._item_sequence_counter + s
                if item_index < len(self._current_order.item_sequence):
                    self._items_selection.append(self._current_order.item_sequence[item_index])
                else:
                    self._items_selection.append(None)
        else:
            # call in env.step
            self._items_selection.remove(itemdict)
            self._items_selection.append(self._items_preview.pop(0))

    def __updateItemsPreview(self) -> None:
        """
        This method updates the items that are known in advance, but cannot be selected.

        Important.
        ----------
        Call this method after `self.__updateItemsSelection`.
        """
        for k in range(self._n_item_selection, self._n_item_preview):
            item_counter = self._item_sequence_counter + k
            item_key = str(item_counter)
            if item_key in self._current_order["order"]["item_sequence"].keys():
                preview_item = self._current_order["order"]["item_sequence"][item_key]
                if preview_item not in self._items_preview:
                    self._items_preview.append(preview_item)
            else:
                n_pure_preview_items = self._n_item_preview - self._n_item_selection
                if not (len(self._items_preview) >= n_pure_preview_items):
                    self._items_preview.append({})

    def __updatePalletVisualization(self, action: dict) -> None:
        item: Item = action["item"]
        flbcoordinates = action["flb_coordinates"]
        orientation = action["orientation"]
        if orientation == 0:
            length = item.length_mm
            width = item.width_mm

        elif orientation == 1:
            length = item.width_mm
            width = item.length_mm

        lc = LC(
            id=item.id,
            sku=item.article,
            type=None,
            length=length,
            width=width,
            height=item.height_mm,
            weight=None,
            position=Position3D(x=flbcoordinates[0], y=flbcoordinates[1], z=flbcoordinates[2]),
        )

        self._visualization.addLoadCarrier(lc)
        self._visualization.updateVisualization()

    def __determineCornerPoints(self, possibleitems: list[Item]) -> dict:
        """
        Determines the corner points for all items that are given.

        Parameters.
        -----------
        possibleitems: list
            Contains the item dictionary of the items that could be selected for palletization.

        Returns.
        --------
        corner_points: list
            The corner points for an item that is specified by its dimension.
        """
        corner_points = {}
        for item in possibleitems:
            if item is not None:
                corner_points[item.article] = {}
                for orientation in range(self._n_orientations):
                    if orientation == 0:
                        length, width, height = item.length_mm, item.width_mm, item.height_mm
                    elif orientation == 1:
                        width, length, height = item.length_mm, item.width_mm, item.height_mm

                    corner_points[item.article][orientation] = self._target_space.getCornerPointsIn3D(
                        (length, width, height)
                    )

        return corner_points

    def setSizeMultiplicator(self, size_multiplicator: tuple) -> None:
        """
        This method is called whenever the RescaleWrapper is used.
        """
        self._size_multiplicator = size_multiplicator
