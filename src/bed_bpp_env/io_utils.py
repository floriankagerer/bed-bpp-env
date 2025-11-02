"""Contains io utils for this package."""

import json
from pathlib import Path

from bed_bpp_env.data_model.order import Order
from bed_bpp_env.data_model.packing_plan import PackingPlan


def load_order_sequence(file_path: Path) -> list[Order]:
    """Loads an order sequence that is stored in the given file path.

    Args:
        file_path (Path): The path to the file that contains the order sequence.

    Returns:
        list[Order]: The deserialized order sequence.
    """
    with open(file_path) as file:
        serialized_order_sequence: dict = json.load(file, parse_int=False)

    order_sequence = []

    for order_key, order_value in serialized_order_sequence.items():
        serialized_with_id: dict = order_value
        serialized_with_id.update({"id": order_key})
        order_i = Order.from_dict(order_value)
        order_sequence.append(order_i)

    return order_sequence


def load_packing_plan_sequence(file_path: Path) -> list[PackingPlan]:
    """Loads a packing plan sequence that is stored in the given file path.

    Args:
        file_path (Path): The path to the file that contains the packing plans.

    Returns:
        list[PackingPlan]: The deserialized packing plan sequence.
    """
    with open(file_path) as file:
        serialized_packing_plan_sequence: dict = json.load(file, parse_int=False)

    packing_plan_sequence = []

    for packing_plan_id, actions in serialized_packing_plan_sequence.items():
        serialized = {"id": packing_plan_id, "actions": actions}
        packing_plan_i = PackingPlan.from_dict(serialized)
        packing_plan_sequence.append(packing_plan_i)

    return packing_plan_sequence
