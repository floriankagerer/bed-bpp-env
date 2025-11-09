"""Module contains functions for setup a scene in Blender."""

import logging
from typing import Optional

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.data_model.type_alias import RGBColor
from bed_bpp_env.evaluation.blender.bpy_helpers.cleanup import cleanup_materials, cleanup_objects
from bed_bpp_env.evaluation.blender.bpy_helpers.populators.box import place_box
from bed_bpp_env.evaluation.blender.bpy_helpers.populators.camera import place_camera
from bed_bpp_env.evaluation.blender.bpy_helpers.populators.floor import place_floor
from bed_bpp_env.evaluation.blender.bpy_helpers.render_settings import draw_object_edges
from bed_bpp_env.evaluation.blender.bpy_helpers.rigid_body import enable_rigid_body_world_simulation
from bed_bpp_env.evaluation.blender.coloring import rgba_from_rgb
from bed_bpp_env.evaluation.blender.target import Target

logger = logging.getLogger(__name__)


def _cleanup_scene(objects_to_keep: Optional[list[str]] = None) -> None:
    """
    Removes objects that have been placed in previous simulations from the Blender template.

    Args:
        objects_to_keep (Optional[list[str]]): The name of the objects that are not removed from the scene,
            e.g., lights.
    """
    cleanup_materials()
    cleanup_objects(objects_to_keep)


def _carry_out_actions(actions: list[Action], item_rgb_color_map: dict[str, RGBColor]) -> None:
    """
    Carries out the given action, i.e., placing the item in at the given position in the given orientation.

    Args:
        actions (list[Action]): The actions that are carried out.
        items_rgb_color_map (dict[str, RGBColor]): The map of the item to the corresponding color.
    """
    for action in actions:
        rgb = item_rgb_color_map.get(action.item.color_identifier)
        color_rgba = rgba_from_rgb(rgb, 1.0)

        place_box(action, color_rgba)


def initialize_scene(
    target: Target,
    actions: list[Action],
    item_rgb_color_map: dict[str, RGBColor],
    objects_to_keep: Optional[list[str]] = None,
) -> None:
    """
    Initializes a scene in Blender.

    Args:
        target (Target): The palletizing target.
        actions (list[Action]): Contains the items and how they are placed in the scene.
        items_rgb_color_map (dict[str, RGBColor]): The map of the item to the corresponding color.
        objects_to_keep (Optional[list[str]]): The name of the objects that are not removed from the scene,
            e.g., lights.
    """
    _cleanup_scene(objects_to_keep)

    enable_rigid_body_world_simulation()
    draw_object_edges()

    place_camera(target)
    place_floor(target=target)
    place_target = target.get_modelling_function_in_blender()
    place_target()

    _carry_out_actions(actions, item_rgb_color_map)
