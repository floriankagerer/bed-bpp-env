"""Main script to convert a packing plan."""

import json
import logging
from pathlib import Path

from bed_bpp_env.data_model.packing_plan import PackingPlan
from bed_bpp_env.integration.banpu_lahcsisr.orientation_reduction import make_equivalent_packing_plans
from bed_bpp_env.io_utils import load_packing_plan_sequence

PACKING_PLAN_PATH = Path(__file__).parents[4] / "assets" / "packing_plans" / "2025-10-28_puphaiboon_banpu_lahcsisr.json"
"""The path to the file that contains the packing plan."""

logger = logging.getLogger(__name__)


def serialize_packing_plan_sequence(packing_plan_sequence: list[PackingPlan]) -> dict:
    """
    Serializes the packing plan sequence.

    Args:


    Returns:
        dict: The serialized packing plan sequence.
    """
    serialized = {}

    for plan in packing_plan_sequence:
        serialized_plan = plan.to_dict()
        serialized.update(serialized_plan)

    return serialized


def write_equivalent_packing_plan_sequence_to_disk(file_path: Path, packing_plan_sequence: list[PackingPlan]) -> None:
    """
    Writes the packing plan sequence to the given file path.

    Args:
        file_path (Path): The path to that the packing plan sequence is written.
        packing_plan_sequence (list[PackingPlan]): The packing plans that are written to disk.
    """
    serialized_packing_plan_sequence = serialize_packing_plan_sequence(packing_plan_sequence)

    with open(file_path, "w") as file:
        json.dump(serialized_packing_plan_sequence, file, indent=2)
    logger.info(f"wrote '{file_path}'")


if __name__ == "__main__":
    logger.info(f"convert the packing plan in '{PACKING_PLAN_PATH}'")

    original_packing_plan_sequence = load_packing_plan_sequence(PACKING_PLAN_PATH)

    equivalent_packing_plan_sequence = make_equivalent_packing_plans(original_packing_plan_sequence)

    equivalent_file_path = PACKING_PLAN_PATH.parent / ("equivalent_" + PACKING_PLAN_PATH.name)
    write_equivalent_packing_plan_sequence_to_disk(equivalent_file_path, equivalent_packing_plan_sequence)
