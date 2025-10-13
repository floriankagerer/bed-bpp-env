from abc import ABC
from dataclasses import dataclass, fields
from typing import Self


@dataclass
class DataclassBase(ABC):
    """Base class for data model that deserializes instances by considering a defined `alias`."""

    @classmethod
    def from_dict(cls, serialized: dict[str, str]) -> Self:
        """Deserialize dictionary into dataclass instance, considering defined `alias`."""
        init_kwargs = {}
        for f in fields(cls):
            alias = f.metadata.get("alias", f.name)
            # Support either the alias or the original name in the input dict
            if alias in serialized:
                init_kwargs[f.name] = serialized[alias]
            elif f.name in serialized:
                init_kwargs[f.name] = serialized[f.name]
        return cls(**init_kwargs)
