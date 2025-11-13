"""Module to reduce the values of orientation to the values that the `PalletizingEnvironment` is capable of."""

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.orientation import Orientation
from bed_bpp_env.data_model.packing_plan import PackingPlan
from bed_bpp_env.integration.banpu_lahcsisr.full_orientation import FullOrientation


def equivalent_item_for_given_orientation(item: Item, orientation: FullOrientation) -> tuple[Item, Orientation]:
    """
    Swaps the item's dimension such that the returned item is equivalent to the original item in the
    given orientation.

    Args:
        item (Item): The original item.
        orientation (FullOrientation): The orientation of the item.

    Returns:
        Item: A reshaped item that is equivalent to the given item with the orientation.
        Orientation: The orientation that is recognized by this package.
    """

    original_length = item.length_mm
    original_width = item.width_mm
    original_height = item.height_mm

    if orientation is FullOrientation.LWH:
        new_length = original_length
        new_width = original_width
        new_height = original_height
    elif orientation is FullOrientation.LHW:
        new_length = original_length
        new_width = original_height
        new_height = original_width
    elif orientation is FullOrientation.WLH:
        new_length = original_width
        new_width = original_length
        new_height = original_height
    elif orientation is FullOrientation.WHL:
        new_length = original_width
        new_width = original_height
        new_height = original_length
    elif orientation is FullOrientation.HLW:
        new_length = original_height
        new_width = original_length
        new_height = original_width
    elif orientation is FullOrientation.HWL:
        new_length = original_height
        new_width = original_width
        new_height = original_length

    equivalent_item = Item(
        article=item.article,
        id=item.id,
        product_group=item.product_group,
        length_mm=new_length,
        width_mm=new_width,
        height_mm=new_height,
        weight_kg=item.weight_kg,
        sequence=item.sequence,
    )

    return (
        equivalent_item,
        Orientation.LWH,
    )


def make_equivalent_packing_plans(packing_plans: list[PackingPlan]) -> list[PackingPlan]:
    """
    Makes equivalent packing plans, i.e., swapping the item dimensions, considering the other orientation
    value `FullOrientation`, to have an equivalent item with an orientation value in `Orientation`.

    Args:
        packing_plans (list[PackingPlan]): The packing plans from the algorithm `banpu` with orientation values in
            `FullOrientation`.

    Returns:
        list[PackingPlan]: The equivalent packing plans.
    """
    equivalent_packing_plans: list[PackingPlan] = []

    for plan in packing_plans:
        equivalent_actions: list[Action] = []

        for action in plan.actions:
            item = action.item
            orientation = FullOrientation(action.orientation)

            equivalent_item, fixed_orientation = equivalent_item_for_given_orientation(
                item=item, orientation=orientation
            )

            eq_action = Action(
                item=equivalent_item, orientation=fixed_orientation, flb_coordinates=action.flb_coordinates
            )

            equivalent_actions.append(eq_action)

        eq_packing_plan = PackingPlan(id=plan.id, actions=equivalent_actions)

        equivalent_packing_plans.append(eq_packing_plan)

    return equivalent_packing_plans
