from enum import StrEnum


class CollisionShape(StrEnum):
    """Collision shapes in Blender.

    Links
    https://docs.blender.org/api/current/bpy_types_enum_items/rigidbody_object_shape_items.html#rna-enum-rigidbody-object-shape-items
    """

    BOX = "BOX"
    """Collision shape box."""
