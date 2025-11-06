from enum import StrEnum
from typing import Self

_TO_METERS = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
}
"""Factor to conver 1 unit into meters."""


class LengthUnit(StrEnum):
    """Enum that contains multiple units for the length."""

    MILLIMETER = "mm"
    CENTIMETER = "cm"
    METER = "m"

    def to_meters(self, length_value: float) -> float:
        """Converts the length value to meters."""
        factor = _TO_METERS[self.value]
        return float(length_value) * factor

    def from_meters(self, meters: float) -> float:
        """Converts the length value in meters to this unit."""
        factor = _TO_METERS[self.value]
        return float(meters) / factor

    def convert(self, length_value: float, target_unit: Self) -> float:
        """Converts the length value from this unit to the target unit."""

        meters = self.to_meters(length_value)

        return target_unit.from_meters(meters)
