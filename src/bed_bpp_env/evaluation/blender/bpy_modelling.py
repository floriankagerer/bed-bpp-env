"""Modelling functions for Blender."""

import math

import bpy  # type: ignore

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.data_model.length_unit import LengthUnit
from bed_bpp_env.data_model.orientation import Orientation
from bed_bpp_env.data_model.type_alias import RGBAColor
from bed_bpp_env.evaluation.blender.bpy_object_properties import (
    assign_material_to_object,
    define_and_get_material,
    get_material_from_bpy_data,
    set_material_and_enable_rigid_body,
    set_rigid_body_settings,
)
from bed_bpp_env.evaluation.blender.collision_shape import CollisionShape

# TODO(florian): Add enum for targets


def _add_euro_pallet_part(position: tuple[float, float, float], size: tuple[float, float, float]) -> None:
    """Adds the part of a Euro-pallet to the scene in Blender."""
    offset_x, offset_y, offset_z = 0, 0, -0.144 - 0.001
    shifted_position = [position[0] + offset_x, position[1] + offset_y, position[2] + size[2] / 2 + offset_z]
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        calc_uvs=True,
        enter_editmode=False,
        align="WORLD",
        location=list(shifted_position),
        rotation=(0.0, 0.0, 0.0),
        scale=size,
    )
    set_material_and_enable_rigid_body("pal_part")


def add_euro_pallet_to_blender() -> None:
    """Adds a Euro-pallet to the Blender bpy contect scene."""
    # Lowest layer
    positions = [(0 + 0.6, 0 + 0.1 / 2, 0), (0 + 0.6, 0.4, 0), (0 + 0.6, 0.8 - 0.1 / 2, 0)]
    sizes = [(1.2, 0.1, 0.022), (1.2, 0.145, 0.022), (1.2, 0.1, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # Lower middle layer
    positions = [
        (0 + 0.145 / 2, 0 + 0.1 / 2, 0.022),
        (0 + 0.145 / 2, 0.4, 0.022),
        (0 + 0.145 / 2, 0.8 - 0.1 / 2, 0.022),
    ]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    positions = [
        (1.2 - 0.145 / 2, 0 + 0.1 / 2, 0.022),
        (1.2 - 0.145 / 2, 0.4, 0.022),
        (1.2 - 0.145 / 2, 0.8 - 0.1 / 2, 0.022),
    ]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    positions = [(0.6, 0 + 0.1 / 2, 0.022), (0.6, 0.4, 0.022), (0.6, 0.8 - 0.1 / 2, 0.022)]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # "Balken" quer
    positions = [(0 + 0.145 / 2, 0.4, 0.1), (0.6, 0.4, 0.1), (1.2 - 0.145 / 2, 0.4, 0.1)]
    sizes = [(0.145, 0.8, 0.022), (0.145, 0.8, 0.022), (0.145, 0.8, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # längsbalken ganz oben breit
    positions = [(0.6, 0 + 0.145 / 2, 0.122), (0.6, 0.4, 0.122), (0.6, 0.8 - 0.145 / 2, 0.122)]
    sizes = [(1.2, 0.145, 0.022), (1.2, 0.145, 0.022), (1.2, 0.145, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # längsbalken ganz oben schmal
    positions = [(0.6, 0.4 - 0.145 / 2 - 0.04 - 0.1 / 2, 0.122), (0.6, 0.4 + 0.145 / 2 + 0.04 + 0.1 / 2, 0.122)]
    sizes = [(1.2, 0.1, 0.022), (1.2, 0.1, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)


def _add_rollcontainer_part(position: tuple[float, float, float], size: tuple[float, float, float]) -> None:
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


def _add_rollcontainer_wheel(xy_position: tuple[float, float]) -> None:
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


def add_rollcontainer_to_blender() -> None:
    """Adds objects to the scene that represent a rollcontainer."""
    # add stripes in x-direction
    sizes = 10 * [(0.8, 0.0367, 0.05)]
    positions = [(0 + size[0] / 2, i * (0.0367 + 0.333 / 9) + size[1] / 2, 0) for i, size in enumerate(sizes)]
    for pos, size in zip(positions, sizes):
        _add_rollcontainer_part(pos, size)

    # add stripes in y-direction
    sizes = 10 * [(0.0367, 0.7, 0.05)]
    positions = [(i * (0.0367 + 0.433 / 9) + size[0] / 2, 0 + size[1] / 2, 0) for i, size in enumerate(sizes)]
    for pos, size in zip(positions, sizes):
        _add_rollcontainer_part(pos, size)

    wheel_positions = [(0.1, 0.1), (0.1, 0.6), (0.7, 0.6), (0.7, 0.1)]
    for pos in wheel_positions:
        _add_rollcontainer_wheel(pos)


def add_box_to_blender(action: Action, color_rgba: RGBAColor) -> None:
    """
    Adds the item to the given position. The item gets the given color assigned.

    Args:
        action (Action): Contains which item is placed, in which location, and in which orientation.
        color_rgba (RGBAColor): The rgba values of the item's color in Blender.
    """
    item = action.item

    orientation = Orientation(action.orientation)

    size_wrt_orientation = orientation.get_item_size(item)
    size_wrt_orientation_in_m = [LengthUnit.MILLIMETER.convert(dim, LengthUnit.METER) for dim in size_wrt_orientation]

    scaled_flb_coordinates = [
        LengthUnit.MILLIMETER.convert(coord, LengthUnit.METER) for coord in action.flb_coordinates.xyz
    ]

    location = [coord + dim / 2 for coord, dim in zip(scaled_flb_coordinates, size_wrt_orientation_in_m)]

    # add the item
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        calc_uvs=True,
        enter_editmode=False,
        align="WORLD",
        location=location,
        rotation=(0.0, 0.0, 0.0),
        scale=size_wrt_orientation_in_m,
    )

    set_rigid_body_settings(enable=True, mass=item.weight_kg, collision_shape=CollisionShape.BOX)

    # Use id for object name
    bpy.context.object.name = f"item_{item.id}"

    # set the color and material, respectively
    ob = bpy.context.active_object

    # Get material
    material = get_material_from_bpy_data(item.id)
    if material is None:
        material = define_and_get_material(item.id, color_rgba)

    assign_material_to_object(ob, material)
