"""Module to cleanup the Blender simulation."""

from typing import Optional

import bpy  # type: ignore


def cleanup_materials() -> None:
    """
    Removes all materials that are stored in `bpy.data.materials`.
    """
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)


def cleanup_objects(objects_to_keep: Optional[list[str]] = None) -> None:
    """
    Removes the objects that are stored in `bpy.data.objects`, except the ones that are given.

    Args:
        objects_to_keep (Optional[list[str]]): The name of the objects that are not removed from `bpy.data.objects`.
    """
    if objects_to_keep is None:
        objects_to_keep = []

    objects_to_keep = [bpy.data.objects.get(name) for name in objects_to_keep]

    for object in bpy.data.objects:
        if object in objects_to_keep:
            continue
        else:
            bpy.data.objects.remove(object)
