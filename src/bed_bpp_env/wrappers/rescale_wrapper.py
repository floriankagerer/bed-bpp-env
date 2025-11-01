"""
This wrapper rescales a gym PalletizingEnvironment. For given divisors of the original observation shape, the

(1) new observation,
(2) allowed area information,
(3) size of the next items, and
(4) the applied actions

are rescaled. This wrapper changes the `reset` and the `step` method of the original environment.
"""

from typing import Optional
import gymnasium as gym
import numpy as np

from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.order import Order


class RescaleWrapper(gym.Wrapper):
    """
    This wrapper creates an environment that has different shapes of the base env's observation.

    Parameters.
    -----------
    size_divisor: tuple (default = `(10, 10)`)
        Defines by which number the size of the original observation is divided. The first number is for the `x`-coordinates, the second for the `y`-coordinates.

    Attributes.
    -----------
    __ACTION_MULTIPLICATOR: dict
        Defines by which number the size of the original observation is divided. Its format is optimized for the transo
    __SIZE_DIVISOR: tuple
        Defines by which number the size of the original observation is divided. Its format is optimized for np.arrays, i.e., it is stored in the way of `(divisor_for_y, divisor_for_x)`.

    Note that the original environment can be accessed by `self.env`.
    """

    def __init__(self, env, size_divisor: tuple = (10, 10)) -> None:
        super().__init__(env)

        self.__SIZE_DIVISOR = (size_divisor[1], size_divisor[0])
        """The divisor of the size as tuple. Note that this attribute can be directly inserted in the numpy array since its dimensions have already been swapped."""

        self.__ACTION_MULTIPLICATOR = {"x": self.__SIZE_DIVISOR[1], "y": self.__SIZE_DIVISOR[0]}
        """This dictionary contains the values that are multiplied by the FBB coordinates of a given action."""

        self.env.setSizeMultiplicator(size_divisor)

    def reset(self, order_sequence: Optional[list[Order]] = None) -> tuple:
        # def reset(self, data_for_episodes={}) -> tuple:
        """
        This method rescales the observation and adapts the information dictionary of the base environment.

        Parameters.
        -----------
        data_for_episodes: dict (default=`{}`)
            The data for the episodes in the format of the benchmark data.

        Returns.
        --------
        rescaledObservation: np.ndarray
            The rescaled observation of the base environment's reset method.
        info: dict
            The adapted information of the base environment's reset method.
        """
        observation, info = self.env.reset(order_sequence)
        rescaledObservation = self.__generateRescaledObservation(observation)
        info["allowed_area"] = self.__rescaleAllowedArea(info["allowed_area"])
        info["next_items_selection"] = self.__rescaleSizeOfNextItems(info["next_items_selection"])
        info["next_items_preview"] = self.__rescaleSizeOfNextItems(info["next_items_preview"])
        return rescaledObservation, info

    def step(self, action: dict) -> tuple:
        """
        This method converts the action to the original size, does a step call of the base environment, obtains the returns of the original step method, rescales the observation and adapts the information dictionary of the base environment.

        Parameters.
        -----------
        action: dict
            The action contains the `"x"` and `"y"` coordinate of the placement as well as the `"orientation"` of the item.

        Returns.
        --------
        rescaledObservation: np.ndarray
            The rescaled observation of the base environment's step method.
        reward: float
            The reward of the base environment's step method.
        done: bool
            The done signal of the base environment's step method.
        info: dict
            The adapted information of the base environment's step method.
        """
        rescaledAction = self.action(action)
        observation, reward, done, info = self.env.step(rescaledAction)
        rescaledObservation = self.__generateRescaledObservation(observation)
        info["allowed_area"] = self.__rescaleAllowedArea(info["allowed_area"])
        info["next_items_selection"] = self.__rescaleSizeOfNextItems(info["next_items_selection"])
        info["next_items_preview"] = self.__rescaleSizeOfNextItems(info["next_items_preview"])
        return rescaledObservation, reward, done, info

    def action(self, originalAction: dict) -> dict:
        """
        The action's values of the `x`- and `y`-coordinate are adjusted to the wrapped environment. Thus, to apply the action to the base environment, we have to multiply the coordinates with the specified divisor.

        Parameters.
        -----------
        originalAction: dict
            The action that is performed to the environment.

        Returns.
        --------
        rescaledAction: dict
            The action where the coordinates in `x` and `y` direction are rescaled to the size of the base environment.
        """
        rescaledAction = {}
        for key, val in originalAction.items():
            if key in self.__ACTION_MULTIPLICATOR.keys():
                rescaledAction[key] = val * self.__ACTION_MULTIPLICATOR[key]
            else:
                rescaledAction[key] = val

        return rescaledAction

    def __rescaleAllowedArea(self, allowedArea: dict) -> dict:
        """
        This method rescales the `np.ndarrays` that contain the allowed areas for an item placement. Since the size of the rescaled observation is smaller than the original size, the values are gathered, i.e., a value in the new observation is the minimum of the values in the old observation.

        Parameters.
        -----------
        allowedArea: dict
            This dictionary contains the allowed area for an item placement. Its keys represent the orientation of the item and its values the corresponding allowed areas.

        Returns.
        --------
        rescaledAllowedArea: dict
            The dictionary that contains the allowed areas in the rescaled size.

        Examples.
        ---------
        >>> allowedArea = {
                # orientation: arrayAllowedAray
                0: np.ndarray,
                1: np.ndarray,
                ...
            }
        """
        rescaledAllowedArea = {}
        for orientation, arrayAllowedArea in allowedArea.items():
            # get the shape
            originalShape = arrayAllowedArea.shape
            rescaledShape = tuple(orShape // divisor for orShape, divisor in zip(originalShape, self.__SIZE_DIVISOR))

            rescaledObs = np.zeros(rescaledShape, dtype=int)
            it = np.nditer(rescaledObs, flags=["multi_index"])
            for _ in it:
                rescaledIdx = it.multi_index
                valRescaledIdx = np.amin(
                    arrayAllowedArea[
                        rescaledIdx[0] * self.__SIZE_DIVISOR[0] : (rescaledIdx[0] + 1) * self.__SIZE_DIVISOR[0],
                        rescaledIdx[1] * self.__SIZE_DIVISOR[1] : (rescaledIdx[1] + 1) * self.__SIZE_DIVISOR[1],
                    ]
                )
                rescaledObs[rescaledIdx] = valRescaledIdx

            # set the rescaled allowed area in the return dict
            rescaledAllowedArea[orientation] = rescaledObs

        return rescaledAllowedArea

    def __generateRescaledObservation(self, observation: np.ndarray) -> np.ndarray:
        """
        We transform the observation of the original environment, where the observation holds the heights in each position in millimeters. Since the size of the rescaled observation is smaller than the original size, the values are gathered, i.e., a value in the new observation is the maximum of the values that are mapped to the new observation.

        Parameters.
        -----------
        observation: np.ndarray
            The original observation of the base environment. Its shape is either (700, 800) or (800, 1200) since the heights of the palletizing target are stored every millimeter.

        Returns.
        --------
        rescaledObs: np.ndarray
            The observation rescaled to the specified size.
        """
        # get the new shape of the observation
        originalShape = observation.shape
        rescaledShape = tuple(orShape // divisor for orShape, divisor in zip(originalShape, self.__SIZE_DIVISOR))

        rescaledObs = np.zeros(rescaledShape, dtype=int)
        it = np.nditer(rescaledObs, flags=["multi_index"])
        for _ in it:
            rescaledIdx = it.multi_index
            valRescaledIdx = np.amax(
                observation[
                    rescaledIdx[0] * self.__SIZE_DIVISOR[0] : (rescaledIdx[0] + 1) * self.__SIZE_DIVISOR[0],
                    rescaledIdx[1] * self.__SIZE_DIVISOR[1] : (rescaledIdx[1] + 1) * self.__SIZE_DIVISOR[1],
                ]
            )
            rescaledObs[rescaledIdx] = valRescaledIdx

        return rescaledObs

    def __rescaleSizeOfNextItems(self, next_items: list[Item]) -> list[Item]:
        """
        Rescales the length and the width of the next items by the given size divisor.

        Parameters.
        -----------
        nextitems: list
            A list of dictionaries that contains the properties of the next items.

        Returns.
        --------
        rescaledNextItems: list
            A list of dictionaries that contains the properties of the next items with rescaled length and width of each item.
        """
        rescaled_next_items = []

        for item in next_items:
            rescaled_item = Item(
                article=item.article,
                id=item.id,
                product_group=item.product_group,
                length_mm=item.length_mm / self.__SIZE_DIVISOR[1],
                width_mm=item.width_mm / self.__SIZE_DIVISOR[0],
                height_mm=item.height_mm,
                weight_kg=item.weight_kg,
                sequence=item.sequence,
            )

            rescaled_next_items.append(rescaled_item)

        return rescaled_next_items
