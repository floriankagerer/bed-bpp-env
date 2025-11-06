"""Responsible for coloring in Blender."""

import json
import logging
from pathlib import Path

from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.type_alias import RGBAColor, RGBColor

logger = logging.getLogger(__name__)


def load_custom_hex_color_map(file_path: Path) -> dict[str, str]:
    with open(file_path) as file:
        custom_hex_color_map = json.load(file, parse_int=False)

    return custom_hex_color_map


def rgb_from_hex(hex: str) -> RGBColor:
    """
    Converts the color from hex in RGB format.

    Args:
        hex (str): A color in hex format.

    Returns:
        RGBColor: The percentage of red, green, and blue in %, i.e., values are in [0, 1].
    """
    r_hex = hex[1:3]
    g_hex = hex[3:5]
    b_hex = hex[5:7]
    return int(r_hex, 16) / 255.0, int(g_hex, 16) / 255.0, int(b_hex, 16) / 255.0


def rgba_from_rgb(rgb: RGBColor, alpha: float) -> RGBAColor:
    """
    Appends the given alpha value to the rgb color. Note that `alpha` must be in [0, 1].

    Args:
        rgb (RGBColor): The rgb color.
        alpha (float): The alpha value.

    Returns:
        RGBAColor: The rgb color with the given alpha value.
    """
    if alpha < 0:
        logger.warning("alpha is smaller than 0 - set alpha=0.0")
        alpha = 0
    elif alpha > 1:
        logger.warning("alpha is bigger than 1 - set alpha=1.0")
        alpha = 1

    r, g, b = rgb
    return (r, g, b, alpha)


def retrieve_rgb_color_for_item(
    custom_hex_color_map: dict[str, str], item_color_name_map: dict[str, str], item: Item
) -> RGBColor:
    """
    Retrieves the color for the given item.

    Args:
        custom_hex_color_map (dict[str, str]): Contains custom color names, e.g., `"own_01"` , as key and a hex value.
        item_color_name_map (dict[str, str]): Contains which item has which custom color name
        item (Item): The item for that the rgb color is retrieved.

    Returns:
        RGBColor: The rgb color that is used for the item.
    """
    color_name = item_color_name_map[item.article]
    hex_str = custom_hex_color_map.get(color_name)
    return rgb_from_hex(hex_str)
