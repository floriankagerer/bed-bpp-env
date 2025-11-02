"""
This script evaluates a packing plan, i.e., a Blender stability check is performed and the KPIs of the packing plan are calculated.
"""

import gc
import logging
import pathlib
import platform
import subprocess
import time

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.data_model.packing_plan import PackingPlan
from bed_bpp_env.evaluation import EVALOUTPUTDIR
from bed_bpp_env.evaluation.blender import TEMPLATEFILE
from bed_bpp_env.evaluation.packing_plan_evaluator import PackingPlanEvaluator
from bed_bpp_env.io_utils import load_packing_plan_sequence
from bed_bpp_env.utils import ENTIRECONFIG

logger = logging.getLogger(__name__)

ppEvaluator = PackingPlanEvaluator()
"""An instance of PackingPlanEvaluator that evaluates the given packing plan."""

EVALCONFIG = ENTIRECONFIG["evaluation"]
"""The configuration for the evaluation."""

# get blender cmd
# cmd = ["blender"] # works only when "blender" is in PATH
if EVALCONFIG["blenderpath"] == "":
    usedPlatform = platform.platform()
    if "macOS" in usedPlatform:
        BLENDERPATH = "/Applications/Blender.app/Contents/MacOS/Blender"
    elif "Linux" in usedPlatform:
        BLENDERPATH = "/snap/blender/current/blender"
    else:
        raise ValueError(f"platform {usedPlatform} is currently not implemented > set blenderpath in bed-bpp_env.conf")
else:
    print(f"use blender path from configuration file")
    BLENDERPATH = EVALCONFIG["blenderpath"]
    if not (pathlib.Path(BLENDERPATH).exists()):
        raise FileNotFoundError(f"check your blender path in bed-bpp_env.conf!")


def evaluate_packing_plan(packing_plan: PackingPlan, order: dict) -> None:
    """
    This methods evaluates the given packing plan with a PackingPlanEvaluator instance.

    Parameters.
    -----------
    id: str
        The id of the order.
    order: dict
        The order that correpsonds to the packing plan that is evaluated.
    packingplan: list
        The packing plan that is evaluated.
    """
    ppEvaluator.evaluate(packing_plan, order)


def run_blender_stability_check(
    background: bool,
    orderid: str,
    renderscene: bool,
    actionplan: list[Action],
    orderofpackingplan: dict,
    ordercolors: dict,
) -> None:
    """
    This method calls blender to create a scene and start a rigid body simulation. Finally, the movement of all items during the simulation time is written to a file. For details see the file that is given by `blenderSceneGen`.

    Parameters.
    -----------
    packingplan: str
        The path to the packing plan as string.
    order: str
        The path to the order as string.
    orderid: str
        The ID of the order.
    actionplan: list
        The list of actions for the given order.
    orderofpackingplan: dict
        The order that was the basis for the given packing plan.
    """
    serialized_actions = [action.to_dict() for action in actionplan]

    templFile = str(TEMPLATEFILE)
    blenderSceneGen = str(TEMPLATEFILE.parent.resolve().joinpath("scene_creation.py"))

    cmd = [BLENDERPATH]

    if background:
        cmd += ["-b"]
    cmd += [
        templFile,
        "--python",
        blenderSceneGen,
        "--",
        "order_number",
        orderid,
        "output_dir",
        EVALOUTPUTDIR,
        "render",
        str(renderscene),
        "order_packing_plan",
        str(serialized_actions),
        "order",
        str(orderofpackingplan),
        "order_colors",
        str(ordercolors),
    ]

    subprocess.run(cmd, shell=False)
    # run garbage collector -> it seems that the run of subprocess leads to a memory leak
    if not (int(orderid) % 10):
        gc.collect()  # run every 10 orders


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    import json

    import bed_bpp_env.utils as utils
    from bed_bpp_env.utils import PARSEDARGUMENTS, getPathToExampleData

    # configure the parser of the given arguments
    parser = utils.arguments_parser.addGroupToParser("EvalPackingPlan", "the arguments of the packing plan evaluation")
    parser.add_argument(
        "--data",
        type=str,
        default=getPathToExampleData().joinpath("5_bed-bpp.json"),
        help="Defines which data is used.",
    )
    parser.add_argument(
        "--packing_plan",
        type=str,
        default=getPathToExampleData().joinpath("packing_plan_5-bed-bpp.json"),
        help="Defines the packing plan that is evaluated.",
    )
    parser.add_argument(
        "-b",
        "--background",
        action="store_false",
        default=True,
        help="Indicates whether the Blender file should be opened.",
    )
    parser.add_argument(
        "-r",
        "--render",
        action="store_true",
        default=False,
        help="Indicates whether the created scenes are written to disk.",
    )
    utils.arguments_parser.parse()
    args = PARSEDARGUMENTS
    logger.info(f"got arguments: {args}")

    packing_plans_path = pathlib.Path(args.get("packing_plan"))
    pathBenData = pathlib.Path(args.get("data"))
    notOpenBlender = args.get("background")

    PACKING_PLANS = load_packing_plan_sequence(packing_plans_path)

    with open(pathBenData) as file:
        BENDATA = json.load(file, parse_int=False)

    totalAmountOfItemsInBendata = 0
    for orderData in BENDATA.values():
        totalAmountOfItemsInBendata += len(orderData["item_sequence"])
    logger.info(f"have {totalAmountOfItemsInBendata} items in {pathBenData}")

    file_color_db = (
        pathlib.Path(__file__).resolve().joinpath(f"../visualization/colors/colordb_{pathBenData.name}").resolve()
    )
    with open(file_color_db) as file:
        COLOR_DB = json.load(file, parse_int=False)

    # Start Evaluation
    for packing_plan in PACKING_PLANS:
        packing_plan_id = packing_plan.id
        bendataOrder = BENDATA.get(packing_plan_id)
        startTime = time.time()
        run_blender_stability_check(
            background=notOpenBlender,
            orderid=packing_plan_id,
            renderscene=args.get("render"),
            actionplan=packing_plan.actions,
            orderofpackingplan=bendataOrder,
            ordercolors=COLOR_DB[packing_plan_id],
        )
        logger.info(f"blender stability check took {round(time.time() - startTime, 3)} seconds")
        evaluate_packing_plan(packing_plan, bendataOrder)
        logger.info(f"complete evaluation of order/packing plan took {round(time.time() - startTime, 3)} seconds")

        # free memory
        del BENDATA[packing_plan_id]
        if not (int(packing_plan_id) % 500):
            gc.collect()

    ppEvaluator.writeToFile(totalAmountOfItemsInBendata)
