"""
Contains helper functions for positions of objects in `bpy`.

Links:
- https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object.matrix_world
"""

import bpy  # type: ignore


def get_position(blend_object: bpy.types.BlendDataObjects) -> tuple[float, float, float]:
    """
    Get the position of the object in Blender.

    Args:
        blend_object (BlendDataObjects): The object for that the position is returned.

    Returns:
        tuple[float, float, float]: The position of the given object.
    """
    return tuple(blend_object.matrix_world.translation)
