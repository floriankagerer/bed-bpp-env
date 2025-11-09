"""
This script generates a scene in a Blender file.

Run in combination with
`blender -b template.blend --python scene_creation.py -- packing-plan <packing-plan>.json data <ben-data>.json order_number 00100021 outputdirectory output/default/evaluation`

The above mentioned command runs Blender in the background (-b) and opens the file `template.blend`, and runs the Python script `scene_creation.py`. The arguments following the Python file are needed by the script.
"""

import logging
from pathlib import Path
from time import perf_counter
from typing import Optional

import bpy  # type: ignore

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.evaluation.blender.bpy_helpers.objects import get_name, get_objects
from bed_bpp_env.evaluation.blender.bpy_helpers.position import get_position
from bed_bpp_env.evaluation.blender.bpy_helpers.scene import get_render_range, get_scene, set_frame
from bed_bpp_env.evaluation.blender.coloring import create_item_rgb_color_map
from bed_bpp_env.evaluation.blender.scene_setup import initialize_scene
from bed_bpp_env.evaluation.blender.target import Target

logger = logging.getLogger(__name__)

CUSTOM_HEX_COLOR_MAP_PATH = Path(__file__).parents[2] / "visualization" / "colors" / "colors.json"
"""The path to the .json file that contains the name of custom hex colors and the corresponding hex value."""

FIXED_OBJECTS = ["Light.000", "Light.001", "Light.002"]


def deserialize_actions(serialized_actions: list[dict]) -> list[Action]:
    """Deserializes the given actions.

    Args:
        serialized_actions (list[dict]): The serialized actions that are deserialized.

    Returns
        list[Action]: The deserialized actions
    """
    return [Action.from_dict(serialized) for serialized in serialized_actions]


def prepare_blender_file(
    target: Target,
    actions: list[Action],
    item_custom_color_name_map: dict[str, str],
    objects_to_keep: Optional[list[str]] = None,
) -> None:
    """
    Prepares the Blender file, i.e., initialize the scene, remove not required objects.

    Args:
        target (Target): The palletizing target.
        actions (list[Action]): Contains the items and how they are placed in the scene.
        item_custom_color_name_map (dict[str, str]): Contains which item has which custom color name.
        objects_to_keep (Optional[list[str]]): The name of the objects that are not removed from the scene,
            e.g., lights.
    """
    custom_hex_color_map = load_custom_hex_color_map(CUSTOM_HEX_COLOR_MAP_PATH)

    items = [action.item for action in actions]
    item_rgb_color_map = create_item_rgb_color_map(
        custom_hex_color_map=custom_hex_color_map, item_custom_color_name_map=item_custom_color_name_map, items=items
    )
    initialize_scene(
        target=target,
        actions=actions,
        item_rgb_color_map=item_rgb_color_map,
        objects_to_keep=objects_to_keep,
    )


def run_simulation() -> None:
    """
    Runs the simulation in Blender by setting every frame. This updates all objects and leads to a correct render and
    rigid body simulation.
    """
    # every frame has to be set in order to have a correct render and rigid body simulation
    start_time = perf_counter()

    first_frame, last_frame = get_render_range()

    scene = get_scene()
    for frame in range(first_frame, last_frame + 1):
        set_frame(scene, frame)

    end_time = perf_counter()
    logger.debug(f"simulation took {end_time - start_time} seconds")


def retrieve_item_positions(
    frames: list[int], objects_to_ignore: Optional[list[str]] = None
) -> dict[str, dict[int, tuple[float, float, float]]]:
    """
    Retrieves the position of the objects for the specified frames.

    Args:
        frames (list[int]): The frames in that we retrieve the location of each item.
        objects_to_ignore (Optional[list[str]]): The name of the objects that are not returned.

    Returns:
        dict[str, dict[int, tuple[float, float, float]]]: The positions of the items in the specified frames.
    """
    # TODO(florian): Introduce data class for positions.

    start_time = perf_counter()

    item_locations = {}

    scene = get_scene()
    focus_objects = get_objects(objects_to_ignore)

    for frame in frames:
        set_frame(scene, frame)

        for obj in focus_objects:
            item_name = get_name(obj)
            item_position = get_position(obj)

            if item_name not in item_locations.keys():
                item_locations[item_name] = {}
            item_locations[item_name][frame] = item_position

    end_time = perf_counter()
    logger.debug(f"retrieved item positions in {end_time - start_time} seconds")

    return item_locations


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    import ast
    import math
    import statistics
    import sys
    import time

    from bed_bpp_env.evaluation.blender.coloring import load_custom_hex_color_map

    blenderMainStart = time.time()
    # get all arguments after "--"
    argsCommandLine = sys.argv[sys.argv.index("--") + 1 :]
    commands = {}
    for i in range(int(len(argsCommandLine) / 2)):
        commands[argsCommandLine[2 * i]] = argsCommandLine[2 * i + 1]

    # check whether the needed arguments were given
    for neededCommand in ["order_number", "order", "order_colors", "order_packing_plan", "output_dir"]:
        if not (neededCommand) in commands:
            raise ValueError(f'argument "{neededCommand}" must be given!')

    # evaluate the str-arguments to expressions
    ORDER_COLORS = ast.literal_eval(commands.get("order_colors"))
    """The colors for the visualization of the given packing plan (dict)."""
    ORDER_PP = ast.literal_eval(commands.get("order_packing_plan"))
    """The packing plan of the given order (list)."""
    ORDER_NUMBER = commands.get("order_number")
    """The id of the current order (str)."""
    ORDER = ast.literal_eval(commands.get("order"))
    """The order for which the packing plan was generated (dict)."""
    RENDER_SCENE = ast.literal_eval(commands.get("render", "False"))
    """This bool indicates whether to render the scene and store it on disk."""
    OUTPUT_DIR = Path(commands.get("output_dir"))
    """The directore where the results are stored (Path)."""

    # # #
    action_plan = deserialize_actions(ORDER_PP)
    target = Target(ORDER["properties"]["target"])

    prepare_blender_file(
        target=target, actions=action_plan, item_custom_color_name_map=ORDER_COLORS, objects_to_keep=FIXED_OBJECTS
    )

    run_simulation()

    first_and_last_frame = get_render_range()

    # retrieve positions of items
    item_positions = retrieve_item_positions(first_and_last_frame, FIXED_OBJECTS)

    # compare the previously stored item locations
    startTime = time.time()
    first_frame, last_frame = first_and_last_frame
    itemMovements = []
    zMovements = []
    for itemName, frameAndPositions in item_positions.items():
        startPos = frameAndPositions.get(first_frame)
        endPos = frameAndPositions.get(last_frame)

        itemDelta = math.dist(startPos, endPos)
        itemMovements.append(itemDelta)

        zMovements.append(abs(startPos[-1] - endPos[-1]))

    logger.debug(f"z movements calculation took \t{round(1000 * (time.time() - startTime))} ms")
    # append the KPIs to a file
    movementValues = {"mean_z-movements/m": statistics.fmean(zMovements), "max_z-movements/m": max(zMovements)}
    evalFile = OUTPUT_DIR.joinpath("stability.txt")

    with open(evalFile, "a") as file:
        file.write(f"{ORDER_NUMBER}:{str(movementValues)}\n")

    # render and store the currently set frames
    if RENDER_SCENE:
        RENDERDIRECTORY = OUTPUT_DIR.joinpath("render/")
        RENDERDIRECTORY.mkdir(exist_ok=True)
        scene = get_scene()
        for frame in first_and_last_frame:
            set_frame(scene, frame)

            renderFilepath = RENDERDIRECTORY.joinpath(f"{ORDER_NUMBER}_frame_{frame}")
            bpy.context.scene.render.filepath = str(renderFilepath)
            bpy.ops.render.render(write_still=True)

    logger.debug(f"scene_creation.py finished after {round(time.time() - blenderMainStart, 3)} seconds")
