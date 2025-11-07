"""Tests for `Orientation`."""

import pytest
from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.orientation import Orientation


@pytest.fixture
def sample_item() -> Item:
    """Fixture that returns a sample item."""
    return Item(
        article="article",
        id="id",
        product_group="product_group",
        length_mm=300,
        width_mm=200,
        height_mm=100,
        weight_kg=3.14,
        sequence=1,
    )


def test_orientation_values() -> None:
    """Tests the values."""
    assert Orientation.LWH == 0
    assert Orientation.WLH == 1


def test_orientation_from_value() -> None:
    """Tests whether an instance is created from value."""
    assert Orientation(0) is Orientation.LWH
    assert Orientation(1) is Orientation.WLH

    with pytest.raises(ValueError):
        Orientation(3.14159265)


@pytest.mark.parametrize(
    "orientation, expected_size", [(Orientation.LWH, (300, 200, 100)), (Orientation.WLH, (200, 300, 100))]
)
def test_orientation_get_item_size_correctness(
    orientation: Orientation, expected_size: tuple[int, int, int], sample_item: Item
) -> None:
    size_wrt_orientation = orientation.get_item_size(item=sample_item)

    assert size_wrt_orientation == expected_size


def test_orientation_get_item_size_completeness(sample_item: Item) -> None:
    """Tests whether for all values of `Orientation` the item size is returned."""
    for orientation in Orientation:
        _ = orientation.get_item_size(item=sample_item)
