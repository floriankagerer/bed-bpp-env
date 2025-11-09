"""
Contains helper functions when working with objects in `bpy.

Links:
- https://docs.blender.org/api/current/bpy.types.BlendData.html#bpy.types.BlendData.objects
"""

from typing import Optional

import bpy  # type: ignore


def get_objects(object_to_ignore: Optional[list[str]] = None) -> list[bpy.types.BlendDataObjects]:
    """
    Returns the objects that are stored in a .blend file.

    Args:
        objects_to_ignore (Optional[list[str]]): The name of the objects that are not returned.

    Returns:
        list[BlendDataObjects]: The objects that are stored in a .blend file.
    """
    all_objects = bpy.data.objects

    return [blend_object for blend_object in all_objects if blend_object not in object_to_ignore]


def get_name(blend_object: bpy.types.BlendDataObjects) -> str:
    """
    Returns the name of the object.

    Args:
        blend_object (BlendDataObjects): The object for that the name is returned.

    Returns:
        str: The name of the object.
    """
    return blend_object.name
