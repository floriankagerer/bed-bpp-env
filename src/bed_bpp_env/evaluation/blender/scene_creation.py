"""
This script generates a scene in a Blender file.

Run in combination with
`blender -b template.blend --python scene_creation.py -- packing-plan <packing-plan>.json data <ben-data>.json order_number 00100021 outputdirectory output/default/evaluation`

The above mentioned command runs Blender in the background (-b) and opens the file `template.blend`, and runs the Python script `scene_creation.py`. The arguments following the Python file are needed by the script.
"""

import bpy
import ast
import json
import logging
import math
import pathlib
import statistics
import sys
import time

logger = logging.getLogger(__name__)

filePath = pathlib.Path(__file__)
colorsPath = filePath.parents[2].resolve().joinpath("visualization/colors/colors.json")
with open(colorsPath) as file:
    OWN_HEX_COLORS = json.load(file, parse_int=False)


ENDFRAME = bpy.context.scene.frame_end
"""The integer of the last frame in the .blend file."""
FIXED_OBJECTS = ["Light.000", "Light.001", "Light.002"]
SCALE_DIVISOR = 1000  # for Blender scene: convert mm to m


def getRGBFromHex(hex: str) -> tuple:
    """
    Converts the color from hex in RGB format.

    Parameters.
    -----------
    hex: str
        The color given in hex format.

    Returns.
    --------
    rgb: tuple
        The percentage of red, green, and blue in %, i.e., values are in [0, 1].

    Example.
    --------
    >>> getRGBFromHex("#FFFFFF")
    (1.0, 1.0, 1.0)
    """
    r_hex = hex[1:3]
    g_hex = hex[3:5]
    b_hex = hex[5:7]
    return int(r_hex, 16) / 255.0, int(g_hex, 16) / 255.0, int(b_hex, 16) / 255.0


def getRGBFromColorName(name: str) -> tuple:
    """For a given name, which is specified in colors.json in the visualization package, the RGB percentages are returned."""
    hexname = OWN_HEX_COLORS.get(name)
    return getRGBFromHex(hexname)


def addItemToScene(properties: dict) -> None:
    """
    Adds an item that is specified by `properties` to the Blender scene.

    Parameters.
    -----------
    properties: dict
        Contains the item's properties.

    Examples.
    ---------
    >>> properties
    {
        "article": "prezel-00107732",
        "id": "001077732",
        "flb": [0, 0, 0],
        "size": [0.59, 0.39, 0.15],
        "weight": 1.23
    }
    """
    # add the item size to the fbb coordinates
    locationValues = [vFLB + vSIZE / 2 for vFLB, vSIZE in zip(properties["flb"], properties["size"])]
    # add the item
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        calc_uvs=True,
        enter_editmode=False,
        align="WORLD",
        location=locationValues,
        rotation=(0.0, 0.0, 0.0),
        scale=properties["size"],
    )

    # add physics
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.enabled = True
    bpy.context.object.rigid_body.mass = properties["weight"]
    bpy.context.object.rigid_body.collision_shape = "BOX"

    # set name
    bpy.context.object.name = f"item_{properties['id'][1:]}"

    # set the color and material, respectively
    ob = bpy.context.active_object

    # Get material
    mat = bpy.data.materials.get(properties["id"])
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name=properties["id"])
        # set the color
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        bsdf = nodes["Principled BSDF"]
        colorname = ORDER_COLORS[properties["article"]]
        color = getRGBFromColorName(colorname)
        color = (color[0], color[1], color[2], 1)
        bsdf.inputs["Base Color"].default_value = color
        mat.diffuse_color = color

    # Assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        ob.data.materials.append(mat)


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
    color = (1, 1, 1, 1)  # color = (0, 0.0684781, 0.278894, 1)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Alpha"].default_value = 1
    bsdf.inputs["Emission Color"].default_value = (1, 1, 1, 1)

    bottomMaterial.diffuse_color = color
    ob = bpy.context.active_object
    ob.data.materials.append(bottomMaterial)

    # set rigid body to passive
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = "PASSIVE"
    bpy.context.object.name = "bottom"


def __setMaterialAndEnableRigidBody(materialname: str) -> None:
    """
    Set the material and enable the rigid body simulation.

    Parameters.
    -----------
    materialname:str
        The name of the used material. Allowed materials are `"rc_part"` and `"pal_part"`.
    """
    if materialname == "rc_part":
        matcolor = (0.0343398, 0.0466651, 0.061246, 1)  # "space gray", HEX:343d46
    elif materialname == "pal_part":
        matcolor = (0.730461, 0.47932, 0.242281, 1)  # "burlywood"

    # set the color and material, respectively
    ob = bpy.context.active_object

    # Get material
    mat = bpy.data.materials.get(materialname)
    if mat is None:
        mat = bpy.data.materials.new(materialname)
        # set the color
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        bsdf = nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = matcolor
        mat.diffuse_color = matcolor

    # assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        ob.data.materials.append(mat)

    # first set material, then enable rigid body
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = "PASSIVE"
    bpy.context.object.name = materialname


def __addPalObject(position: list, size: list) -> None:
    offsetX, offsetY, offsetZ = 0, 0, -0.144 - 0.001
    translatedPosition = [position[0] + offsetX, position[1] + offsetY, position[2] + size[2] / 2 + offsetZ]
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        calc_uvs=True,
        enter_editmode=False,
        align="WORLD",
        location=list(translatedPosition),
        rotation=(0.0, 0.0, 0.0),
        scale=size,
    )
    __setMaterialAndEnableRigidBody("pal_part")


def addEURPallet() -> None:
    # add lowest layer
    positions = [(0 + 0.6, 0 + 0.1 / 2, 0), (0 + 0.6, 0.4, 0), (0 + 0.6, 0.8 - 0.1 / 2, 0)]
    sizes = [(1.2, 0.1, 0.022), (1.2, 0.145, 0.022), (1.2, 0.1, 0.022)]
    for pos, size in zip(positions, sizes):
        __addPalObject(pos, size)

    # add lower middle layer
    positions = [
        (0 + 0.145 / 2, 0 + 0.1 / 2, 0.022),
        (0 + 0.145 / 2, 0.4, 0.022),
        (0 + 0.145 / 2, 0.8 - 0.1 / 2, 0.022),
    ]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        __addPalObject(pos, size)

    positions = [
        (1.2 - 0.145 / 2, 0 + 0.1 / 2, 0.022),
        (1.2 - 0.145 / 2, 0.4, 0.022),
        (1.2 - 0.145 / 2, 0.8 - 0.1 / 2, 0.022),
    ]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        __addPalObject(pos, size)

    positions = [(0.6, 0 + 0.1 / 2, 0.022), (0.6, 0.4, 0.022), (0.6, 0.8 - 0.1 / 2, 0.022)]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        __addPalObject(pos, size)

    # balken quer
    positions = [(0 + 0.145 / 2, 0.4, 0.1), (0.6, 0.4, 0.1), (1.2 - 0.145 / 2, 0.4, 0.1)]
    sizes = [(0.145, 0.8, 0.022), (0.145, 0.8, 0.022), (0.145, 0.8, 0.022)]
    for pos, size in zip(positions, sizes):
        __addPalObject(pos, size)

    # längsbalken ganz oben breit
    positions = [(0.6, 0 + 0.145 / 2, 0.122), (0.6, 0.4, 0.122), (0.6, 0.8 - 0.145 / 2, 0.122)]
    sizes = [(1.2, 0.145, 0.022), (1.2, 0.145, 0.022), (1.2, 0.145, 0.022)]
    for pos, size in zip(positions, sizes):
        __addPalObject(pos, size)

    # längsbalken ganz oben schmak
    positions = [(0.6, 0.4 - 0.145 / 2 - 0.04 - 0.1 / 2, 0.122), (0.6, 0.4 + 0.145 / 2 + 0.04 + 0.1 / 2, 0.122)]
    sizes = [(1.2, 0.1, 0.022), (1.2, 0.1, 0.022)]
    for pos, size in zip(positions, sizes):
        __addPalObject(pos, size)


def __addRCObject(position: list, size: list) -> None:
    offsetX, offsetY, offsetZ = 0, 0, -0.05
    translatedPosition = position[0] + offsetX, position[1] + offsetY, position[2] + size[2] / 2 + offsetZ
    bpy.ops.mesh.primitive_cube_add(
        size=1, enter_editmode=False, align="WORLD", location=list(translatedPosition), scale=size
    )
    __setMaterialAndEnableRigidBody("rc_part")


def __addRCWheels(xyposition: tuple) -> None:
    """
    Adds wheels of the rollcontainer to the given position.

    Parameters.
    -----------
    xyposition: tuple
        The (x,y) position of the wheel.
    """
    position = (xyposition[0], xyposition[1], -0.11)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,
        depth=0.075,
        enter_editmode=False,
        align="WORLD",
        location=[0, 0, 0],
        rotation=((90.0 / 180.0 * 3.14159265), (90.0 / 180.0 * 3.14159265), (90.0 / 180.0 * 3.14159265)),
        scale=(1, 1, 1),
    )
    ob = bpy.context.active_object
    ob.location = position
    __setMaterialAndEnableRigidBody("rc_part")


def addRollcontainer() -> None:
    """Adds objects to the scene that represent a rollcontainer."""
    # add stripes in x-direction
    sizes = 10 * [(0.8, 0.0367, 0.05)]
    positions = [(0 + size[0] / 2, i * (0.0367 + 0.333 / 9) + size[1] / 2, 0) for i, size in enumerate(sizes)]
    for pos, size in zip(positions, sizes):
        __addRCObject(pos, size)

    # add stripes in y-direction
    sizes = 10 * [(0.0367, 0.7, 0.05)]
    positions = [(i * (0.0367 + 0.433 / 9) + size[0] / 2, 0 + size[1] / 2, 0) for i, size in enumerate(sizes)]
    for pos, size in zip(positions, sizes):
        __addRCObject(pos, size)

    wheelPositions = [(0.1, 0.1), (0.1, 0.6), (0.7, 0.6), (0.7, 0.1)]
    for pos in wheelPositions:
        __addRCWheels(pos)


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
        addRollcontainer()
    elif target == "euro-pallet":
        addEURPallet()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
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
    OUTPUT_DIR = pathlib.Path(commands.get("output_dir"))
    """The directore where the results are stored (pathlib.Path)."""

    # get packing plan and color db for order
    startTime = time.time()
    target = ORDER["properties"]["target"]
    __initScene(target)
    logger.debug(f"init scene loading took \t{round(1000 * (time.time() - startTime))} ms")

    # iterate over packing plan
    for i, action in enumerate(ORDER_PP):
        item = action["item"]
        orientation = action["orientation"]
        if orientation == 0:
            size = (
                item["length/mm"] / SCALE_DIVISOR,
                item["width/mm"] / SCALE_DIVISOR,
                item["height/mm"] / SCALE_DIVISOR,
            )
        elif orientation == 1:
            size = (
                item["width/mm"] / SCALE_DIVISOR,
                item["length/mm"] / SCALE_DIVISOR,
                item["height/mm"] / SCALE_DIVISOR,
            )

        flb = []
        for coord in action["flb_coordinates"]:
            flb.append(coord / SCALE_DIVISOR)

        properties = {
            "size": size,
            "flb": flb,
            "weight": item["weight/kg"],
            "id": item["id"],
            "article": item["article"],
        }

        addItemToScene(properties)

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
            if not (itemName in FIXED_OBJECTS):
                if not (itemName in itemLocations.keys()):
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
