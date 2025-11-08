"""Modelling functions for Blender."""

import bpy  # type: ignore

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.data_model.length_unit import LengthUnit
from bed_bpp_env.data_model.orientation import Orientation
from bed_bpp_env.data_model.type_alias import RGBAColor
from bed_bpp_env.evaluation.blender.bpy_helpers.data_model.collision_shape import CollisionShape
from bed_bpp_env.evaluation.blender.bpy_helpers.materials import (
    assign_material_to_object,
    define_material,
    get_material_from_bpy_data,
)
from bed_bpp_env.evaluation.blender.bpy_object_properties import set_rigid_body_settings


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

    flb_coordinates_in_m = [
        LengthUnit.MILLIMETER.convert(coord, LengthUnit.METER) for coord in action.flb_coordinates.xyz
    ]

    location = [coord + dim / 2 for coord, dim in zip(flb_coordinates_in_m, size_wrt_orientation_in_m)]

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
        material = define_material(item.id, color_rgba)

    assign_material_to_object(ob, material)
