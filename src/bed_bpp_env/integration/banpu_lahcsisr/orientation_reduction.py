"""Module to reduce the values of orientation to the values that the `PalletizingEnvironment` is capable of."""

from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.orientation import Orientation
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
