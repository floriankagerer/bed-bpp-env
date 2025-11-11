"""Tests the module `orientation_reduction`."""

import pytest

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.data_model.item import Item
from bed_bpp_env.data_model.orientation import Orientation
from bed_bpp_env.data_model.packing_plan import PackingPlan
from bed_bpp_env.data_model.position_3d import Position3D
from bed_bpp_env.integration.banpu_lahcsisr.full_orientation import FullOrientation
from bed_bpp_env.integration.banpu_lahcsisr.orientation_reduction import (
    equivalent_item_for_given_orientation,
    make_equivalent_packing_plans,
)


@pytest.fixture
def sample_item() -> Item:
    """A sample item."""
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


@pytest.mark.parametrize(
    "orientation, expected_lwh",
    [
        (FullOrientation.LWH, (300, 200, 100)),
        (FullOrientation.LHW, (300, 100, 200)),
        (FullOrientation.WLH, (200, 300, 100)),
        (FullOrientation.WHL, (200, 100, 300)),
        (FullOrientation.HLW, (100, 300, 200)),
        (FullOrientation.HWL, (100, 200, 300)),
    ],
)
def test_equivalent_item_for_given_orientation(
    sample_item: Item, orientation: FullOrientation, expected_lwh: tuple[int, int, int]
) -> None:
    """Tests whether the dimensions are correctly swapped to retrieve an equivalent item."""
    expected_length, expected_width, expected_height = expected_lwh

    equivalent_item, actual_orientation = equivalent_item_for_given_orientation(
        item=sample_item, orientation=orientation
    )

    expected_item = Item(
        article=sample_item.article,
        id=sample_item.id,
        product_group=sample_item.product_group,
        length_mm=expected_length,
        width_mm=expected_width,
        height_mm=expected_height,
        weight_kg=sample_item.weight_kg,
        sequence=sample_item.sequence,
    )
    assert equivalent_item == expected_item
    assert actual_orientation is Orientation.LWH


def test_make_equivalent_packing_plans(sample_item: Item) -> None:
    """Tests whether an equivalent packing plan is made."""
    # 5 == HWL
    original_orientation = FullOrientation(5)
    expected_length, expected_width, expected_height = (
        sample_item.height_mm,
        sample_item.width_mm,
        sample_item.length_mm,
    )

    original_packing_plans = [
        PackingPlan(
            id="test_packing_plan",
            actions=[
                Action(item=sample_item, orientation=original_orientation, flb_coordinates=Position3D(x=100, y=90, z=0))
            ],
        )
    ]

    equivalent_packing_plans = make_equivalent_packing_plans(packing_plans=original_packing_plans)

    expected_item = Item(
        article=sample_item.article,
        id=sample_item.id,
        product_group=sample_item.product_group,
        length_mm=expected_length,
        width_mm=expected_width,
        height_mm=expected_height,
        weight_kg=sample_item.weight_kg,
        sequence=sample_item.sequence,
    )

    expected_packing_plans = [
        PackingPlan(
            id="test_packing_plan",
            actions=[
                Action(item=expected_item, orientation=Orientation.LWH, flb_coordinates=Position3D(x=100, y=90, z=0))
            ],
        )
    ]

    assert equivalent_packing_plans == expected_packing_plans
