"""
This script generates a scene in a Blender file.

Run in combination with
`blender -b template.blend --python scene_creation.py -- packing-plan <packing-plan>.json data <ben-data>.json order_number 00100021 outputdirectory output/default/evaluation`

The above mentioned command runs Blender in the background (-b) and opens the file `template.blend`, and runs the Python script `scene_creation.py`. The arguments following the Python file are needed by the script.
"""

import logging
from pathlib import Path

import bpy  # type: ignore

from bed_bpp_env.data_model.action import Action
from bed_bpp_env.evaluation.blender.bpy_modelling import add_euro_pallet_to_blender, add_rollcontainer_to_blender

logger = logging.getLogger(__name__)

CUSTOM_HEX_COLOR_MAP_PATH = Path(__file__).parents[2] / "visualization" / "colors" / "colors.json"
"""The path to the .json file that contains the name of custom hex colors and the corresponding hex value."""

ENDFRAME = bpy.context.scene.frame_end
"""The integer of the last frame in the .blend file."""
FIXED_OBJECTS = ["Light.000", "Light.001", "Light.002"]


def __addGround(size: tuple = (500, 500, 1), target: str = "euro-pallet") -> None:
    """Adds a ground plane to the scene."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, enter_editmode=False, align="WORLD", location=(0, 0, 0))
    # scale argument does not work here
    bpy.ops.transform.resize(
        value=size,
        orient_type="GLOBAL",
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        orient_matrix_type="GLOBAL",
        mirror=False,
        use_proportional_edit=False,
        proportional_edit_falloff="SMOOTH",
        proportional_size=1,
        use_proportional_connected=False,
        use_proportional_projected=False,
    )
    if target == "euro-pallet":
        zOffsetGround = -0.144 - 0.002
    elif target == "rollcontainer":
        zOffsetGround = -0.05 - 0.11 - 0.001
    bpy.ops.transform.translate(value=(0, 0, zOffsetGround))

    # set the color
    bottomMaterial = bpy.data.materials.new(name="bottom_color")
    bottomMaterial.use_nodes = True
    tree = bottomMaterial.node_tree
    nodes = tree.nodes
    bsdf = nodes["Principled BSDF"]
    # make the bottom "transparent" -> white
    color = (1, 1, 1, 1)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Alpha"].default_value = 1
    # TODO(florian): Fix KeyError: key "Emission Color" not found!
    # bsdf.inputs["Emission Color"].default_value = (1, 1, 1, 1)

    bottomMaterial.diffuse_color = color
    ob = bpy.context.active_object
    ob.data.materials.append(bottomMaterial)

    # set rigid body to passive
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = "PASSIVE"
    bpy.context.object.name = "bottom"


def __initScene(target: str) -> None:
    """Initializes the scene."""
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

    # enable the rigidbody world such that the simulation is enabled
    bpy.context.scene.rigidbody_world.enabled = True
    bpy.context.scene.rigidbody_world.collection = bpy.data.collections["Collection"]

    # draw border of objects
    bpy.context.scene.render.use_freestyle = True

    objsNotToRemove = []
    for objName in FIXED_OBJECTS:
        objsNotToRemove.append(bpy.data.objects.get(objName))
    for obj in bpy.data.objects:
        if not (obj) in objsNotToRemove:
            bpy.data.objects.remove(obj)

    # init the camera
    if target == "rollcontainer":
        camPosition = (2.3388, -2.3318, 2.1809)
    elif target == "euro-pallet":
        camPosition = (2.6788, -2.4603, 2.1692)
    bpy.ops.object.camera_add(
        enter_editmode=False,
        align="VIEW",
        location=camPosition,
        rotation=(1.22872, -4.53789e-07, 0.642278),
        scale=(1, 1, 1),
    )
    bpy.context.object.name = "Camera"
    bpy.context.scene.camera = bpy.context.object

    __addGround(target=target)
    if target == "rollcontainer":
        add_rollcontainer_to_blender()
    elif target == "euro-pallet":
        add_euro_pallet_to_blender()


def deserialize_actions(serialized_actions: list[dict]) -> list[Action]:
    """Deserializes the given actions.

    Args:
        serialized_actions (list[dict]): The serialized actions that are deserialized.

    Returns
        list[Action]: The deserialized actions
    """
    return [Action.from_dict(serialized) for serialized in serialized_actions]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    import ast
    import math
    import statistics
    import sys
    import time

    from bed_bpp_env.evaluation.blender.bpy_modelling import add_box_to_blender
    from bed_bpp_env.evaluation.blender.coloring import (
        load_custom_hex_color_map,
        retrieve_rgb_color_for_item,
        rgba_from_rgb,
    )

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

    custom_hex_color_map = load_custom_hex_color_map(CUSTOM_HEX_COLOR_MAP_PATH)

    # get packing plan and color db for order
    startTime = time.time()
    target = ORDER["properties"]["target"]
    __initScene(target)
    logger.debug(f"init scene loading took \t{round(1000 * (time.time() - startTime))} ms")

    # iterate over packing plan
    for i, action in enumerate(action_plan):
        # retrieve rgba color for item
        rgb = retrieve_rgb_color_for_item(
            custom_hex_color_map=custom_hex_color_map, item_color_name_map=ORDER_COLORS, item=action.item
        )
        color_rgba = rgba_from_rgb(rgb, 1.0)

        add_box_to_blender(action, color_rgba)

    # TODO(florian): Move these lines in a module called bpy_simulation
    # every frame has to be set in order to have a correct render and rigid body simulation
    startTime = time.time()
    scene = bpy.context.scene
    for f in range(ENDFRAME + 1):
        scene.frame_set(f)
    logger.debug(f"frame set took \t\t\t{round(1000 * (time.time() - startTime))} ms")

    # store the item locations for start and endframe
    startTime = time.time()
    itemLocations = {}
    frames4investigation = [0, ENDFRAME]
    for f in frames4investigation:
        # set the correct frame
        scene = bpy.context.scene
        scene.frame_set(f)

        # get the locations of each item
        frameLocations = {}
        for obj in bpy.data.objects:
            itemName = obj.name
            if itemName not in FIXED_OBJECTS:
                if itemName not in itemLocations.keys():
                    itemLocations[itemName] = {}
                itemLocations[itemName][f] = list(obj.matrix_world.translation)

    # compare the previously stored item locations
    itemMovements = []
    zMovements = []
    for itemName, frameAndPositions in itemLocations.items():
        startPos = frameAndPositions.get(frames4investigation[0])
        endPos = frameAndPositions.get(frames4investigation[-1])

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
        for f in frames4investigation:
            scene = bpy.context.scene
            scene.frame_set(f)

            renderFilepath = RENDERDIRECTORY.joinpath(f"{ORDER_NUMBER}_frame_{f}")
            bpy.context.scene.render.filepath = str(renderFilepath)
            bpy.ops.render.render(write_still=True)

    logger.debug(f"scene_creation.py finished after {round(time.time() - blenderMainStart, 3)} seconds")
