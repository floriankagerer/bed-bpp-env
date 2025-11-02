from dataclasses import dataclass, fields
from typing import Self

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.data_model.dataclass_base import DataclassBase


@dataclass
class PackingPlan(DataclassBase):
    """
    Represents a packing plan, i.e., a list of actions to palletize items.
    """

    id: str
    """The identifier of this packing plan."""

    actions: list[Action]
    """The actions of this packing plan."""

    @classmethod
    def from_dict(cls, serialized: dict[str, str | list[dict]]) -> Self:
        """Deserialize dictionary into dataclass instance."""
        init_kwargs = {}
        for f in fields(cls):
            key = f.name

            if key == "actions":
                action_sequence = [Action.from_dict(serialized_action) for serialized_action in serialized[key]]
                init_kwargs[key] = action_sequence

            else:
                init_kwargs[key] = serialized[key]

        return cls(**init_kwargs)
