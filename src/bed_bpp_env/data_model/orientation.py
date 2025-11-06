from enum import IntEnum

from bed_bpp_env.data_model.item import Item


class Orientation(IntEnum):
    """Defines the orientation of items."""

    LWH = 0
    """The item's original orientation."""

    WLH = 1
    """Swap length and width."""

    def get_item_size(self, item: Item) -> tuple[int, int, int]:
        """
        Returns the size of an item with respect to the provided orientation.

        Args:
            item (Item): The item for that the size with respect to the orientation is returned.

        Returns:
            tuple[int,int,int]: The length, width, and height of the item if it has the provided orientation.
        """
        if self is Orientation.LWH:
            size = item.length_mm, item.width_mm, item.height_mm

        elif self is Orientation.WLH:
            size = item.width_mm, item.length_mm, item.height_mm

        else:
            raise NotImplementedError(f"'get_item_size' is not implented for '{self}'")

        return size
