from dataclasses import dataclass, fields
from typing import Self

from bed_bpp_env.data_model.dataclass_base import DataclassBase
from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.position_3d import Position3D


@dataclass
class Action(DataclassBase):
    """An action represents which item is placed, in which location, and in which orientation."""

    item: Item
    """The item that is placed with this action."""
    orientation: int
    """The orientation of the item."""
    flb_coordinates: Position3D
    """The position of the item of this action."""

    @classmethod
    def from_dict(cls, serialized: dict[str, str | list[dict]]) -> Self:
        """Deserialize dictionary into dataclass instance."""
        init_kwargs = {}
        for f in fields(cls):
            key = f.name

            if key == "item":
                init_kwargs[key] = Item.from_dict(serialized[key])

            elif key == "flb_coordinates":
                init_kwargs[key] = Position3D(*serialized[key])

            else:
                init_kwargs[key] = serialized[key]

        return cls(**init_kwargs)

    def to_dict(self) -> dict:
        """Converts the object to a dictionary."""
        as_dict = {
            "item": self.item.to_dict(),
            "orientation": self.orientation,
            "flb_coordinates": list(self.flb_coordinates.xyz),
        }
        return as_dict
