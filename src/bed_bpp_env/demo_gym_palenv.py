"""
This script demonstrates the use of our PalletizingEnvironment in addition to our evaluation with Blender.
"""

import logging
from pathlib import Path

import bed_bpp_env.utils as utils
import bed_bpp_env.utils.arguments_parser as arguments_parser

# configure the parser of the given arguments
parser = arguments_parser.addGroupToParser("DemoGymPalEnv", "the arguments of the gym PalletizingEnvironment demo")
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
arguments_parser.parse()

logger = logging.getLogger(__name__)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    import json
    import subprocess

    from bed_bpp_env.environment.palletizing_environment import PalletizingEnvironment
    from bed_bpp_env.heuristics.lowest_area import LowestArea
    from bed_bpp_env.io_utils import load_order_sequence
    from bed_bpp_env.wrappers.equally_distributed_reward_wrapper import EquallyDistributedRewardWrapper
    from bed_bpp_env.wrappers.rescale_wrapper import RescaleWrapper

    logger.info(f"given arguments: {utils.PARSEDARGUMENTS}")
    logger.info(f"the results are stored in {utils.OUTPUTDIRECTORY}")

    # CHOOSE YOUR HEURISTIC
    heuristic = LowestArea()

    order_data_path = utils.PARSEDARGUMENTS["data"]
    with open(order_data_path) as f:
        ORDERS_FOR_EPISODES = json.load(f, parse_int=False)

    order_sequence = load_order_sequence(order_data_path)

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
    EVALUATION_SCRIPT_PATH = Path(__file__).parent / "script_evaluate_packing_plan.py"
    cmd = [
        "python3",
        EVALUATION_SCRIPT_PATH.as_posix(),
        "--data",
        utils.PARSEDARGUMENTS["data"],
        "--packing_plan",
        utils.OUTPUTDIRECTORY.joinpath("packing_plans.json"),
        "-r",
    ]
    subprocess.run(cmd, shell=False)
