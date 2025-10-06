"""Tests the module `lc`."""

import pytest
from bed_bpp_env.environment.lc import LC


def test_lc_dataclass() -> None:
    """Tests whether an LC object is correctly initialized."""
    lc = LC(
        id="my_lc",
        sku="my_sku",
        type="carton",
        length=300,
        width=200,
        height=100,
        weight=3.14,
        position={"area": None, "x": 2, "y": 1, "z": 0},
    )

    assert lc.id == "my_lc"
    assert lc.sku == "my_sku"
    assert lc.type == "carton"

    assert lc.length == 300
    assert lc.width == 200
    assert lc.height == 100
    assert isinstance(lc.dimensions, tuple)
    assert lc.dimensions == (300, 200, 100)

    assert lc.weight == pytest.approx(3.14)

    assert lc.position == {"area": None, "x": 2, "y": 1, "z": 0}
