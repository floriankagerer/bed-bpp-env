'''
This script runs the heuristic solver `heuristics.O3DBP_3_2`.  
'''
import utils, utils.arguments_parser

# configure the parser of the given arguments
parser = utils.arguments_parser.addGroupToParser("DemoGymPalEnv", "the arguments of the gym PalletizingEnvironment demo")
parser.add_argument("-d", "--debug", action="store_true", default=False, help="Indicates whether the simulation is debugged.")
parser.add_argument("-v", "--visualize", action="store_true", default=False, help="Indicates whether the simulation is visualized.")
parser.add_argument("--vis_debug", action="store_true", default=False, help="Indicates whether all visualizations should be displayed.")
parser.add_argument("--task", type=str, default="O3DBP-3-2", help="Defines the palletizing task.")
parser.add_argument("--data", type=str, default=utils.getPathToExampleData().joinpath("5_bed-bpp.json"), help="Defines which data is used.")
utils.arguments_parser.parse()


import json
import logging
logger = logging.getLogger(__name__)
from heuristics import O3DBP_3_2
import environment.PalletizingEnvironment, environment.LC, environment.SimPalEnv
import subprocess


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

if __name__ == "__main__":
    logger.info(f"given arguments: {utils.PARSEDARGUMENTS}")
    logger.info(f"the results are stored in {utils.OUTPUTDIRECTORY}")

    # init heuristic
    _, nPreview, nSelection = utils.PARSEDARGUMENTS.get("task").split("-")
    heuristic = O3DBP_3_2(preview=int(nPreview), selection=int(nSelection))


    dirOutputfile = utils.PARSEDARGUMENTS["data"] 
    with open(dirOutputfile) as f:
        ORDERS_FOR_EPISODES = json.load(f, parse_int=False)

    # setup a simulation palletizing environment
    env = environment.PalletizingEnvironment()
    observation, info = env.reset(data_for_episodes=ORDERS_FOR_EPISODES)
    simenv = environment.SimPalEnv()
    _, _ = simenv.reset(data_for_episodes = ORDERS_FOR_EPISODES)
    heuristic.setSimEnv(simenv)

    # start simulation
    simDone = False
    while not(simDone):
        env.render()
        action, successful = heuristic.getAction(observation, info) # User-defined policy function
        if successful:
            observation, reward, episodeDone, info = env.step(action)
        else:
            episodeDone = True
        

        if episodeDone:
            env.render()
            observation, info = env.reset()
            _, _ = simenv.reset()
            heuristic.setSimEnv(simenv)
            if info["all_orders_considered"]:
                simDone = True

    env.close()

    # run evaluation
    cmd = ["python3", "script_evaluate_packing_plan.py", "--data", utils.PARSEDARGUMENTS["data"], "--packing_plan", utils.OUTPUTDIRECTORY.joinpath("packing_plans.json")]
    subprocess.run(cmd, shell=False)