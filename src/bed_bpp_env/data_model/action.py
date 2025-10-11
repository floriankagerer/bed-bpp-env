from dataclasses import dataclass

from bed_bpp_env.data_model.position_3d import Position3D


@dataclass
class Action(object):
    """An action represents which item is placed, in which location, and in which orientation."""

    item: dict
    """The item that is placed with this action."""
    orientation: int
    """The orientation of the item."""
    position: Position3D
    """The position of the item of this action."""
