"""Responsible for coloring in Blender."""

from bed_bpp_env.data_model.type_alias import RGBColor


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
