"""
This script demonstrates the use of our PalletizingEnvironment in addition to our evaluation with Blender.
"""

import utils, utils.arguments_parser

# configure the parser of the given arguments
parser = utils.arguments_parser.addGroupToParser(
    "DemoGymPalEnv", "the arguments of the gym PalletizingEnvironment demo"
)
parser.add_argument(
    "-d", "--debug", action="store_true", default=False, help="Indicates whether the simulation is debugged."
)
parser.add_argument(
    "-v", "--visualize", action="store_true", default=False, help="Indicates whether the simulation is visualized."
)
parser.add_argument(
    "--vis_debug", action="store_true", default=False, help="Indicates whether all visualizations should be displayed."
)
parser.add_argument("--task", type=str, default="O3DBP", help="Defines the task.")
parser.add_argument(
    "--data", type=str, default=utils.getPathToExampleData().joinpath("5_bed-bpp.json"), help="Defines the used data."
)
utils.arguments_parser.parse()

import json
import logging
from heuristics import LowestArea
import subprocess

logger = logging.getLogger(__name__)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    from bed_bpp_env.environment.palletizing_environment import PalletizingEnvironment
    from bed_bpp_env.wrappers.equally_distributed_reward_wrapper import EquallyDistributedRewardWrapper
    from bed_bpp_env.wrappers.rescale_wrapper import RescaleWrapper

    logger.info(f"given arguments: {utils.PARSEDARGUMENTS}")
    logger.info(f"the results are stored in {utils.OUTPUTDIRECTORY}")

    # CHOOSE YOUR HEURISTIC
    heuristic = LowestArea()

    dirOutputfile = utils.PARSEDARGUMENTS["data"]
    with open(dirOutputfile) as f:
        ORDERS_FOR_EPISODES = json.load(f, parse_int=False)

    # USE IMPLEMENTED WRAPPERS
    base_env = PalletizingEnvironment()
    env = RescaleWrapper(base_env)  # base_env = env.env
    env = EquallyDistributedRewardWrapper(env)

    observation, info = env.reset(data_for_episodes=ORDERS_FOR_EPISODES)

    for _ in range(1000):
        env.render()
        action = heuristic.getAction(observation, info)  # User-defined policy function
        observation, reward, episodeDone, info = env.step(action)

        if episodeDone:
            env.render()
            observation, info = env.reset()
            if info["all_orders_considered"]:
                break

    env.close()

    # run evaluation
    cmd = [
        "python3",
        "script_evaluate_packing_plan.py",
        "--data",
        utils.PARSEDARGUMENTS["data"],
        "--packing_plan",
        utils.OUTPUTDIRECTORY.joinpath("packing_plans.json"),
        "-r",
    ]
    subprocess.run(cmd, shell=False)
