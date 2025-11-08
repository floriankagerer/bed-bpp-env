"""Module contains function for configuring the render of Blender."""

import bpy  # type: ignore


def draw_object_edges() -> None:
    """Draw stylized strokes using Freestyle

    Links
    - https://docs.blender.org/api/current/bpy.types.RenderSettings.html#bpy.types.RenderSettings.use_freestyle
    """
    bpy.context.scene.render.use_freestyle = True
