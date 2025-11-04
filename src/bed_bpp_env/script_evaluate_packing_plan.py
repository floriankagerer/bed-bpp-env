"""
This script evaluates a packing plan, i.e., a Blender stability check is performed and the KPIs of the packing plan
are calculated.
"""

import gc
import logging
from pathlib import Path

from bed_bpp_env.data_model.order import Order
from bed_bpp_env.io_utils import load_order_sequence

logger = logging.getLogger(__name__)

ARG_NAME_ORDER_PATH = "data"
ARG_NAME_PACKING_PLAN_PATH = "packing_plan"
ARG_NAME_BLENDER_BACKGROUND = "background"
ARG_NAME_RENDER_SCENE = "render"


def unpack_parsed_arguments(args: dict[str, Path | bool]) -> tuple[Path, Path, bool]:
    """
    Unpacks the parsed arguments.

    Args:
        args (dict[str, Path | bool]): The arguments that are parsed.

    Returns:
        Path: The path to the file that contains the order sequence.
        Path: The path to the file that contains the packing plans.
        bool: Indicates whether Blender is run in background.
        bool: Indicates whether the scene is rendered.

    """
    order_sequence_path: Path = args.get(ARG_NAME_ORDER_PATH)
    packing_plans_path: Path = args.get(ARG_NAME_PACKING_PLAN_PATH)
    run_blender_in_background: bool = args.get(ARG_NAME_BLENDER_BACKGROUND)
    render_scene: bool = args.get(ARG_NAME_RENDER_SCENE)

    return order_sequence_path, packing_plans_path, run_blender_in_background, render_scene


def run_garbage_collector() -> None:
    """It seems that the run of subprocess leads to a memory leak. To this end, we explicitely collect the garbage."""
    logger.info("Collect garbage.")
    gc.collect()


def get_number_of_items_in_order_sequence(order_sequence: list[Order]) -> int:
    """Returns the total number of items in the given order sequence.

    Args:
        order_sequence (list[Order]): The order sequence for that the items are counted.

    Returns:
        int: The number of items in the order sequence.
    """
    count = 0
    for order in order_sequence:
        count += len(order.item_sequence)
    return count


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    import json
    import time

    import bed_bpp_env.utils as utils
    from bed_bpp_env.evaluation import EVALOUTPUTDIR
    from bed_bpp_env.evaluation.blender.configuration import retrieve_blender_path
    from bed_bpp_env.evaluation.blender.stability_check import run_blender_stability_check_in_subprocess
    from bed_bpp_env.evaluation.packing_plan_evaluator import PackingPlanEvaluator
    from bed_bpp_env.io_utils import load_packing_plan_sequence
    from bed_bpp_env.utils import ENTIRECONFIG, PARSEDARGUMENTS, getPathToExampleData

    # configure the parser of the given arguments
    parser = utils.arguments_parser.addGroupToParser("EvalPackingPlan", "the arguments of the packing plan evaluation")
    parser.add_argument(
        f"--{ARG_NAME_ORDER_PATH}",
        type=str,
        default=getPathToExampleData().joinpath("5_bed-bpp.json"),
        help="Defines which data is used.",
    )
    parser.add_argument(
        f"--{ARG_NAME_PACKING_PLAN_PATH}",
        type=str,
        default=getPathToExampleData().joinpath("packing_plan_5-bed-bpp.json"),
        help="Defines the packing plan that is evaluated.",
    )
    parser.add_argument(
        "-b",
        f"--{ARG_NAME_BLENDER_BACKGROUND}",
        action="store_false",
        default=True,
        help="Indicates whether the Blender file should be opened.",
    )
    parser.add_argument(
        "-r",
        f"--{ARG_NAME_RENDER_SCENE}",
        action="store_true",
        default=False,
        help="Indicates whether the created scenes are written to disk.",
    )
    utils.arguments_parser.parse()
    args = PARSEDARGUMENTS
    logger.info(f"got arguments: {args}")

    order_sequence_path, packing_plans_path, run_blender_in_background, render_scene = unpack_parsed_arguments(args)

    PACKING_PLANS = load_packing_plan_sequence(packing_plans_path)
    order_sequence = load_order_sequence(order_sequence_path)

    with open(order_sequence_path) as file:
        BENDATA = json.load(file, parse_int=False)

    number_of_items_in_order_sequence = get_number_of_items_in_order_sequence(order_sequence)
    logger.info(f"have {number_of_items_in_order_sequence} items in {order_sequence_path}")

    file_color_db = (
        Path(__file__).resolve().joinpath(f"../visualization/colors/colordb_{order_sequence_path.name}").resolve()
    )
    with open(file_color_db) as file:
        COLOR_DB = json.load(file, parse_int=False)

    packing_plan_evaluator = PackingPlanEvaluator()
    evaluation_configuration = ENTIRECONFIG["evaluation"]

    blender_path = retrieve_blender_path(evaluation_configuration)

    # Start Evaluation
    for i, packing_plan in enumerate(PACKING_PLANS):
        packing_plan_id = packing_plan.id
        order = BENDATA.get(packing_plan_id)
        startTime = time.time()
        run_blender_stability_check_in_subprocess(
            blender_path=blender_path,
            order=order,
            packing_plan=packing_plan,
            output_dir=EVALOUTPUTDIR,
            colors=COLOR_DB[packing_plan.id],
            run_blender_in_background=run_blender_in_background,
            render_scene=render_scene,
        )
        logger.info(f"blender stability check took {round(time.time() - startTime, 3)} seconds")
        # Check whether to collect garbage
        if not (i % 10) and i:
            run_garbage_collector()

        # evaluate packing plan with evaluator
        packing_plan_evaluator.evaluate(packing_plan, order)
        logger.info(f"complete evaluation of order/packing plan took {round(time.time() - startTime, 3)} seconds")

        # free memory
        del BENDATA[packing_plan_id]
        if not (i % 500) and i:
            run_garbage_collector()

        break

    packing_plan_evaluator.writeToFile(number_of_items_in_order_sequence)
