"""Convenience functions for working with `bpy.data`."""

from typing import Optional

import bpy  # type: ignore

from bed_bpp_env.data_model.type_alias import RGBAColor


def delete_all_materials_in_bpy_data() -> None:
    """
    Removes all materials that are stored in `bpy.data.materials`.
    """
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)


def delete_objects_from_bpy_data(objects_to_keep: Optional[list[str]] = None) -> None:
    """
    Removes the objects that are stored in `bpy.data.objects`, except the ones that are given.

    Args:
        objects_to_keep (Optional[list[str]]): The name of the objects that are not removed from `bpy.data.objects`.
    """
    objects_to_keep = [bpy.data.objects.get(name) for name in objects_to_keep]

    for object in bpy.data.objects:
        if object in objects_to_keep:
            continue
        else:
            bpy.data.objects.remove(object)


def get_material_from_bpy_data(material_name: str) -> Optional[bpy.types.Material]:
    """
    Returns the material that is stored in `bpy.data.materials` with the given name. If no material with the name
    is stored, `None` is returned.

    Args:
        material_name (str): The name of the material.

    Returns:
        Optional[bpy.types.Material]: The material with the given name, or `None` if no material has the specified name.
    """
    return bpy.data.materials.get(material_name)


def define_material(material_name: str, material_color: RGBAColor) -> bpy.types.Material:
    """
    Defines a new material with the given name and sets the color to the given value.

    Args:
        material_name (str): The name of the material.
        material_color (RGBAColor): The RGBA value of the material's color.

    Returns:
        Material: The defined material.

    Links:
        Material: https://docs.blender.org/api/current/bpy.types.Material.html
    """
    # define new material
    material = bpy.data.materials.new(material_name)

    # set color of material
    material.use_nodes = True
    tree_nodes = material.node_tree.nodes
    bsdf = tree_nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = material_color
    material.diffuse_color = material_color

    return material
