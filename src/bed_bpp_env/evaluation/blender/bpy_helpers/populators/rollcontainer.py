"""Module that contains functions to place a rollcontainer in Blender."""

import math

import bpy  # type: ignore

from bed_bpp_env.evaluation.blender.bpy_object_properties import set_material_and_enable_rigid_body


def _place_rollcontainer_part(position: tuple[float, float, float], size: tuple[float, float, float]) -> None:
    offset_x, offset_y, offset_z = 0, 0, -0.05
    shifted_position = position[0] + offset_x, position[1] + offset_y, position[2] + size[2] / 2 + offset_z
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        enter_editmode=False,
        align="WORLD",
        location=list(shifted_position),
        scale=size,
    )
    set_material_and_enable_rigid_body("rc_part")


def _place_rollcontainer_wheel(xy_position: tuple[float, float]) -> None:
    """
    Adds a wheel of the rollcontainer to the given position.

    Args:
        xy_position (tuple[float, float]): The `(x, y)` position of the wheel. The z-coordinate is fixed.
    """
    position = (xy_position[0], xy_position[1], -0.11)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,
        depth=0.075,
        enter_editmode=False,
        align="WORLD",
        location=[0, 0, 0],
        rotation=((90.0 / 180.0 * math.pi), (90.0 / 180.0 * math.pi), (90.0 / 180.0 * math.pi)),
        scale=(1, 1, 1),
    )

    active_object = bpy.context.active_object
    active_object.location = position

    set_material_and_enable_rigid_body("rc_part")


def place_rollcontainer() -> None:
    """Adds objects to the scene that represent a rollcontainer."""
    # add stripes in x-direction
    sizes = 10 * [(0.8, 0.0367, 0.05)]
    positions = [(0 + size[0] / 2, i * (0.0367 + 0.333 / 9) + size[1] / 2, 0) for i, size in enumerate(sizes)]
    for pos, size in zip(positions, sizes):
        _place_rollcontainer_part(pos, size)

    # add stripes in y-direction
    sizes = 10 * [(0.0367, 0.7, 0.05)]
    positions = [(i * (0.0367 + 0.433 / 9) + size[0] / 2, 0 + size[1] / 2, 0) for i, size in enumerate(sizes)]
    for pos, size in zip(positions, sizes):
        _place_rollcontainer_part(pos, size)

    wheel_positions = [(0.1, 0.1), (0.1, 0.6), (0.7, 0.6), (0.7, 0.1)]
    for pos in wheel_positions:
        _place_rollcontainer_wheel(pos)
