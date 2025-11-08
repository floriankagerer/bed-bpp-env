"""Module that contains functions to place a camera in Blender."""

import bpy  # type: ignore

from bed_bpp_env.evaluation.blender.target import Target


def place_camera(target: Target) -> None:
    """
    Places the camera in Blender. Its pose depends on the given target.

    Args:
        target (Target): The palletizing target.
    """
    camera_position, camera_rotation = target.get_camera_pose_in_blender()
    bpy.ops.object.camera_add(
        enter_editmode=False,
        align="VIEW",
        location=camera_position,
        rotation=camera_rotation,
        scale=(1, 1, 1),
    )
    bpy.context.object.name = "Camera"
    bpy.context.scene.camera = bpy.context.object
