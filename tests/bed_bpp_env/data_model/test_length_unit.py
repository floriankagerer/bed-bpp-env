"""Tests the module `LengthUnit`."""

from pytest import approx

from bed_bpp_env.data_model.length_unit import LengthUnit


def test_length_unit_factors_for_all_values_present() -> None:
    """Tests whether for all length units we can retrieve the factors for conversion."""
    for unit in LengthUnit:
        _ = unit.to_meters(3.14)


def test_length_unit_convert() -> None:
    millimeter = LengthUnit.METER.convert(3.14, LengthUnit.MILLIMETER)
    assert millimeter == approx(3140.0)

    meter = LengthUnit.MILLIMETER.convert(123, LengthUnit.METER)
    assert meter == approx(0.123)
