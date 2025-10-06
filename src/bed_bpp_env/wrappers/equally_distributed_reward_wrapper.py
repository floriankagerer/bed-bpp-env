"""
This wrapper distribtues the reward equally in each call of `step`.
"""

import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
from bed_bpp_env.utils import PARSEDARGUMENTS

VISUALIZE_REWARD_DISTRIBUTION = PARSEDARGUMENTS.get("vis_debug", False)


class EquallyDistributedRewardWrapper(gym.Wrapper):
    """
    This wrapper creates an environment that distributes equally the reward in each `step`.

    Parameters.
    -----------
    env: gym.Env
        The environment that is wrapped. Note that it can be accessed by `wrappedenv.env`.

    Attributes.
    -----------
    __N_ITEMS_IN_ORDER: int
        Holds the amount of items that are in the currently treated item sequence.
    __Rewards: dict
        Holds the original rewards and the new values of them.
    """

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)

        self.__N_ITEMS_IN_ORDER = None
        """The amount of items in an order. It is set whenever the method `reset` is called."""

        self.__Rewards = {"old": None, "new": None}
        """This dictionary contains two lists. The list of the key `"old"` holds the rewards that `self.env` returns. The list with the key `"new"` contains the values of the reward that are calculated by this wrapper."""

    def __calculateReward(self) -> float:
        """Calculate the reward and return it."""
        return 1.0 / (self.__N_ITEMS_IN_ORDER)

    def reset(self, data_for_episodes={}) -> tuple:
        """
        If `VISUALIZE_REWARD_DISTRIBUTION` is set to `True`, a plot is displayed that shows the original (=old) reward, the new values of the reward and the accumulative value of the new reward. Note that the `plt.show()` methods blocks the simulation!


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
        if not (self.__Rewards["old"] is None) and VISUALIZE_REWARD_DISTRIBUTION:
            self.__visualizeDistributedReward()

        observation, info = self.env.reset(data_for_episodes)
        self.__N_ITEMS_IN_ORDER = info.get("n_items_in_order", np.inf)
        self.__resetRewardDict()

        return observation, info

    def step(self, action: dict) -> tuple:
        """
        This method converts the action to the original size, does a step call of the base environment, obtains the returns of the original step method, rescales the observation and adapts the information dictionary of the base environment.

        Parameters.
        -----------
        action: dict
            The action that is performed on the environment.

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
        observation, reward, done, info = self.env.step(action)
        newReward = self.__calculateReward()
        self.__Rewards["old"].append(reward)
        self.__Rewards["new"].append(newReward)

        return observation, newReward, done, info

    def __visualizeDistributedReward(self) -> None:
        x = np.arange(0, 1 + len(self.__Rewards["new"]))

        fig = plt.figure(__name__)
        fig.clf()

        plt.step(x, [0] + self.__Rewards["new"], label="new", where="post")
        accumulatedReward = [sum(self.__Rewards["new"][: i + 1]) for i, _ in enumerate(self.__Rewards["new"])]
        plt.step(x, [0] + accumulatedReward, where="post", label="acc. new")
        plt.step(x, [0] + self.__Rewards["old"], label="old", alpha=0.5)

        plt.grid(axis="both")
        plt.legend(title="reward:")
        xLabels = [str(xi) if not (xi % 5) or xi == x[-1] else "" for xi in x]
        plt.xticks(x, labels=xLabels)
        plt.xlabel("placed items")
        plt.ylabel(r"reward after placing item $i$")

        # blocking
        # plt.show()
        # non blocking
        plt.draw()
        plt.pause(0.001)
        # plt.close()

    def __resetRewardDict(self) -> None:
        """Resets the attribute that stores the rewards."""
        self.__Rewards = {"old": [], "new": []}
