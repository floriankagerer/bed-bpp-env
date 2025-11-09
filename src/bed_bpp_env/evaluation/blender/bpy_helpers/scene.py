"""
Module contains functions for working with a scene in Blender.

Links
- https://docs.blender.org/api/current/bpy.types.Scene.html#bpy.types.Scene.frame_set

"""

import bpy  # type: ignore


def get_scene() -> bpy.types.Scene:
    """
    Returns the scene data-block.

    Returns:
        Scene: Scene data-block, consisting in objects and defining time and render related settings.
    """
    return bpy.context.scene


def set_frame(scene: bpy.types.Scene, frame_number: int) -> None:
    """
    Set scene frame updating all objects and view layers immediately.

    Args:
        scene (Scene): Scene data-block, consisting in objects and defining time and render related settings.
        frame_number (int): The frame number to set.
    """
    scene.frame_set(frame_number)


def get_render_range() -> tuple[int, int]:
    """
    Returns the render range, i.e., the first frame and the final frame.

    Returns:
        tuple[int, int]: The frame number of the first frame and the frame number of the final frame.

    Links
    - https://docs.blender.org/api/current/bpy.types.Scene.html#bpy.types.Scene.frame_start
    - https://docs.blender.org/api/current/bpy.types.Scene.html#bpy.types.Scene.frame_end
    """
    first_frame = bpy.context.scene.frame_start
    final_frame = bpy.context.scene.frame_end

    return first_frame, final_frame
