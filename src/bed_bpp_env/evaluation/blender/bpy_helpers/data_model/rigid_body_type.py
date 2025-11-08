from enum import StrEnum


class RigidBodyType(StrEnum):
    """Role of object in rigid body simulations.

    Links
    https://docs.blender.org/api/current/bpy.types.RigidBodyObject.html#bpy.types.RigidBodyObject.type
    https://docs.blender.org/api/current/bpy_types_enum_items/rigidbody_object_type_items.html#rna-enum-rigidbody-object-type-items
    """

    PASSIVE = "PASSIVE"
    """Object is directly controlled by animation system."""

    ACTIVE = "ACTIVE"
    """Object is directly controlled by simulation results."""
