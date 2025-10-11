"""Tests the module `item`."""

import pytest

from bed_bpp_env.data_model.item import Item


def test_item_serialization() -> None:
    """Tests whether an object of the dataclass `Item` is correctly serialized."""
    item = Item(
        article="article_test",
        id="id_test",
        product_group="product_group_test",
        length_mm=300,
        width_mm=200,
        height_mm=100,
        weight_kg=3.14,
        sequence=1,
    )

    serialized_item = {
        "article": "article_test",
        "id": "id_test",
        "product_group": "product_group_test",
        "length/mm": 300,
        "width/mm": 200,
        "height/mm": 100,
        "weight/kg": 3.14,
        "sequence": 1,
    }

    assert item.to_dict() == serialized_item


@pytest.mark.parametrize(
    "serialized_item, expected_item",
    [
        (
            {
                "article": "article",
                "id": "id",
                "product_group": "pg",
                "length/mm": 300,
                "width/mm": 200,
                "height/mm": 100,
                "weight/kg": 3.14,
                "sequence": 1,
            },
            Item(
                article="article",
                id="id",
                product_group="pg",
                length_mm=300,
                width_mm=200,
                height_mm=100,
                weight_kg=3.14,
                sequence=1,
            ),
        ),
        (
            {
                "article": "article",
                "id": "id",
                "product_group": "pg",
                "length_mm": 300,
                "width_mm": 200,
                "height_mm": 100,
                "weight_kg": 3.14,
                "sequence": 1,
            },
            Item(
                article="article",
                id="id",
                product_group="pg",
                length_mm=300,
                width_mm=200,
                height_mm=100,
                weight_kg=3.14,
                sequence=1,
            ),
        ),
    ],
)
def test_item_deserialization(serialized_item: dict[str, str | int | float], expected_item: Item) -> None:
    """Tests whether an object of the dataclass `Item` is correctly deserialized."""
    deserialized = Item.from_dict(serialized_item)

    assert deserialized == expected_item
