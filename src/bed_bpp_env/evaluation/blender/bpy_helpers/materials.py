"""
Contains helper functions when working with materials in bpy.

Links
- https://docs.blender.org/api/current/bpy.types.Material.html
"""

from typing import Optional

import bpy  # type: ignore

from bed_bpp_env.data_model.type_alias import RGBAColor


def delete_all_materials_in_bpy_data() -> None:
    """
    Removes all materials that are stored in `bpy.data.materials`.
    """
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)


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


def assign_material_to_object(active_object: bpy.types.Object, material: bpy.types.Material) -> None:
    """
    Assigns the material to the given object.

    Args:
        active_object (Object): The object to that the material is assigned.
        material (Material): The material.

    Links:
        Object: https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object
        Material: https://docs.blender.org/api/current/bpy.types.Material.html
    """
    if active_object.data.materials:
        # Assign to 1st material slot
        active_object.data.materials[0] = material
    else:
        # no slots
        active_object.data.materials.append(material)
