"""tba"""

from enum import IntEnum


class FullOrientation(IntEnum):
    """
    Describes how the dimensions of an item changes. Originally, we define an item's dimensions as
    `(length, width, height)` and `(L, W, H)`, respectively.
    """

    LWH = 0
    """No rotation. New dimensions are as original, i.e., `(L, W, H)`."""

    LHW = 1
    """Rotation around x-axis. New dimensions are `(L, H, W)`."""

    WLH = 2
    """Rotation around z-axis. New dimensions are `(W, L, H)`."""

    WHL = 3
    """Rotation around y-axis. New dimensions are `(W, H, L)`."""

    HLW = 4
    """Complex rotation 1. New dimensions are `(H, L, W)`."""

    HWL = 5
    """Complex rotation 2. New dimensions are `(H, W, L)`."""
