"""Functions for setting properties, e.g., materials, in the Blender scene."""

from typing import Optional

import bpy  # type: ignore

from bed_bpp_env.data_model.type_alias import RGBAColor
from bed_bpp_env.evaluation.blender.bpy_data import get_material_from_bpy_data
from bed_bpp_env.evaluation.blender.collision_shape import CollisionShape
from bed_bpp_env.evaluation.blender.rigid_body_type import RigidBodyType

# TODO(florian): When defining targets, retrieve material names in enum!--Define enum for materials--


def define_and_get_material(material_name: str, material_color: RGBAColor) -> bpy.types.Material:
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


def set_rigid_body_settings(
    enable: bool = False,
    mass: Optional[float] = None,
    collision_shape: Optional[CollisionShape] = None,
    rigid_body_type: Optional[RigidBodyType] = None,
) -> None:
    """
    Sets object settings that are related to the rigid body simulation.

    Args:
        enable (bool): Indicates whether rigid body is enabled.
            https://docs.blender.org/api/current/bpy.types.RigidBodyObject.html#bpy.types.RigidBodyObject.enabled
        mass (Optional[float]): The mass of the object. If `None`, Blender's default value is used (1.0).
            https://docs.blender.org/api/current/bpy.types.RigidBodyObject.html#bpy.types.RigidBodyObject.mass
        collision_shape (Optional[CollisionShape]): The collision shape of the object. If `None`, Blender's default
            value is used ("BOX").
            https://docs.blender.org/api/current/bpy.types.RigidBodyObject.html#bpy.types.RigidBodyObject.collision_shape
        rigid_body_type (Optional[RigidBodyType]): The type of the rigid body object. If `None`, Blender's default value
            is used ("ACTIVE").
            https://docs.blender.org/api/current/bpy.types.RigidBodyObject.html#bpy.types.RigidBodyObject.type
    """

    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.enabled = enable
    if mass is not None:
        bpy.context.object.rigid_body.mass = mass
    if collision_shape is not None:
        bpy.context.object.rigid_body.collision_shape = collision_shape
    if rigid_body_type is not None:
        bpy.context.object.rigid_body.type = rigid_body_type


def set_material_and_enable_rigid_body(material_name: str) -> None:
    """
    Sets the material and enables the rigid body simulation.

    Args:
        material_name (str): The name of the used material.
    """
    if material_name == "rc_part":
        color = (0.0343398, 0.0466651, 0.061246, 1)  # "space gray", HEX:343d46
    elif material_name == "pal_part":
        color = (0.730461, 0.47932, 0.242281, 1)  # "burlywood"

    active_object = bpy.context.active_object

    material = get_material_from_bpy_data(material_name)
    if material is None:
        material = define_and_get_material(material_name, color)

    assign_material_to_object(active_object, material)
    set_rigid_body_settings(rigid_body_type=RigidBodyType.PASSIVE)

    bpy.context.object.name = material_name
