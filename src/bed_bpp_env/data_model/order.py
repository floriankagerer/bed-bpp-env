from __future__ import annotations

from dataclasses import dataclass, field, fields

from bed_bpp_env.data_model.dataclass_base import DataclassBase
from bed_bpp_env.data_model.item import Item


@dataclass
class Properties(DataclassBase):
    """Properties of an order."""

    id: str
    """An additional identifier of an order."""
    order_number: str = field(metadata={"alias": "order_nr"})
    """The order number."""
    type: str
    """The type of this order, e.g., `chilled frozen grocery`."""
    target: str
    """The target of an order."""


@dataclass
class Order(object):
    """
    An order is the input for solving a three-dimensional bin packing problem.
    """

    id: str
    """The identifier of the order."""
    item_sequence: list[Item]
    """The items that have to be packed."""
    properties: Properties
    """Additional information about the order."""

    @classmethod
    def from_dict(cls, serialized: dict[str, str | int | None]) -> Order:
        """Deserialize dictionary into dataclass instance."""
        init_kwargs = {}
        for f in fields(cls):
            key = f.name

            if key == "item_sequence":
                item_sequence = [Item.from_dict(serialized_item) for serialized_item in serialized[key].values()]
                init_kwargs[key] = item_sequence

            elif key == "properties":
                serialized_properties = serialized[key]
                init_kwargs[key] = Properties.from_dict(serialized_properties)

            else:
                init_kwargs[key] = serialized[key]

        return cls(**init_kwargs)
