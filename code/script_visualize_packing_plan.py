"""
This script visualizes a packing plan, which is given as dict with order ids as key and a list of actions as values, and finally creates a video of the palletization for each order.
"""

import utils

# configure the parser of the given arguments
parser = utils.arguments_parser.addGroupToParser("VisPackingPlan", "the arguments of the packing plan visualization")
parser.add_argument(
    "--algo",
    type=str,
    default="DEMO ALGO (add your algorithm name)",
    help="The name of the algorithm that created the packing plan.",
)
parser.add_argument("--algo_prefix", type=str, default="algo", help="A prefix for the created video.")
parser.add_argument(
    "--data",
    type=str,
    default=utils.getPathToExampleData().joinpath("5_bed-bpp.json"),
    help="Defines which data is used.",
)
parser.add_argument(
    "--packing_plan",
    type=str,
    default=utils.getPathToExampleData().joinpath("packing_plan_5-bed-bpp.json"),
    help="Defines the packing plan that is visualized.",
)
utils.arguments_parser.parse()

import json
import pathlib


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    from bed_bpp_env.environment.lc import LC
    from bed_bpp_env.visualization.palletizing_environment_visualization import PalletizingEnvironmentVisualization
    from bed_bpp_env.visualization.video import Video

    # prepare
    packingPlan = pathlib.Path(utils.PARSEDARGUMENTS.get("packing_plan"))
    orderData = pathlib.Path(utils.PARSEDARGUMENTS.get("data"))
    videoPrefix = utils.PARSEDARGUMENTS.get("algo_prefix")
    algoName = utils.PARSEDARGUMENTS.get("algo")

    # load
    with open(packingPlan) as file:
        PACKING_PLAN = json.load(file, parse_int=False)

    with open(orderData) as file:
        SRC_ORDER = json.load(file, parse_int=False)

    # simulate
    for orderID, actions in PACKING_PLAN.items():
        target = SRC_ORDER[orderID]["properties"]["target"]
        vis = PalletizingEnvironmentVisualization(visID=orderID, target=target, algo=algoName)
        vis.setDisplayTime(1)

        for i, action in enumerate(actions):
            item, flb, orientation = action["item"], action["flb_coordinates"], action["orientation"]
            lcProps = {
                "cont_id": item["id"],
                "length": item["length/mm"] if orientation == 0 else item["width/mm"],
                "width": item["width/mm"] if orientation == 0 else item["length/mm"],
                "height": item["height/mm"],
                "sku": item["article"],
            }
            lcTarget = {"area": "area", "x": flb[0], "y": flb[1], "z": flb[2]}

            lc = LC(lcProps)
            lc.setTargetposition(lcTarget)

            vis.addLoadCarrier(lc)
            vis.updateVisualization()
            vis.displayVisualization()

        vis.saveStoredImages()
        listOfImages = vis.getImages4Video()
        videoMaker = Video(f"{videoPrefix}_video_{orderID}.mp4")
        videoMaker.makeVideo(listOfImages)
