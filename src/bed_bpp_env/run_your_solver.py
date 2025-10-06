"""
This script is ready to fill in your solver and run a simulation.
"""

import logging
import bed_bpp_env.utils as utils

# configure the parser of the given arguments
parser = utils.arguments_parser.addGroupToParser(
    "RunYourSolver", "The arguments of your script that evaluates your solver."
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
parser.add_argument("--task", type=str, default="O3DBP-1-1", help="Defines the palletizing task.")
parser.add_argument(
    "--data",
    type=str,
    default=utils.getPathToExampleData().joinpath("5_bed-bpp.json"),
    help="Defines which data is used.",
)
utils.arguments_parser.parse()

logger = logging.getLogger(__name__)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    import json
    from pathlib import Path
    import subprocess

    from bed_bpp_env.environment.palletizing_environment import PalletizingEnvironment

    # # # # # # # # # # # # #
    # load your solver here #
    # # # # # # # # # # # # #
    from solver import your_solver

    logger.info(f"given arguments: {utils.PARSEDARGUMENTS}")
    logger.info(f"the results are stored in {utils.OUTPUTDIRECTORY}")

    # # # # # # # # # # # # # # # #
    # initialize your solver here #
    # # # # # # # # # # # # # # # #
    yourSolver = your_solver()

    dirOutputfile = utils.PARSEDARGUMENTS["data"]
    with open(dirOutputfile) as f:
        ORDERS_FOR_EPISODES = json.load(f, parse_int=False)

    env = PalletizingEnvironment()
    observation, info = env.reset(data_for_episodes=ORDERS_FOR_EPISODES)

    # start simulation
    simDone = False
    while not (simDone):
        env.render()
        # # # # # # # # # # # # # # # # # # # #
        # get the action of your solver here  #
        # # # # # # # # # # # # # # # # # # # #
        action, successful = yourSolver.getAction(observation, info)  # User-defined policy function
        if successful:
            observation, reward, episodeDone, info = env.step(action)
        else:
            episodeDone = True

        if episodeDone:
            env.render()
            observation, info = env.reset()
            if info["all_orders_considered"]:
                simDone = True

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
    ]
    subprocess.run(cmd, shell=False)
