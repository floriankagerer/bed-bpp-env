from __future__ import annotations

from dataclasses import dataclass, field, fields

from bed_bpp_env.data_model.dataclass_base import DataclassBase


@dataclass
class Item(DataclassBase):
    """Represents an object that has to be packed and that is part of an order."""

    article: str
    """The article name of this item."""
    id: str
    """The identifier of this item."""
    product_group: str
    """The product group this item belongs to."""
    length_mm: int = field(metadata={"alias": "length/mm"})
    """The length of this item in millimeters."""
    width_mm: int = field(metadata={"alias": "width/mm"})
    """The width of this item in millimeters."""
    height_mm: int = field(metadata={"alias": "height/mm"})
    """The height of this item in millimeters."""
    weight_kg: float = field(metadata={"alias": "weight/kg"})
    """The weight of this item in kilograms."""
    sequence: int
    """The position of this item within the item sequence."""

    def to_dict(self) -> dict[str, str | int | float]:
        """Converts the object to a dictionary."""
        item_to_dict = {}

        for item_field in fields(self):
            key = item_field.metadata.get("alias", item_field.name)
            item_to_dict[key] = getattr(self, item_field.name)

        return item_to_dict
