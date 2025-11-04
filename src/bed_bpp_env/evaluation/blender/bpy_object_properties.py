"""Functions for setting properties, e.g., materials, in the Blender scene."""

import bpy  # type: ignore

# TODO(florian): Define enum for materials


def set_material_and_enable_rigid_body(material_name: str) -> None:
    """
    Sets the material and enables the rigid body simulation.

    Args:
        material_name (str): The name of the used material.
    """
    if material_name == "rc_part":
        matcolor = (0.0343398, 0.0466651, 0.061246, 1)  # "space gray", HEX:343d46
    elif material_name == "pal_part":
        matcolor = (0.730461, 0.47932, 0.242281, 1)  # "burlywood"

    # set the color and material, respectively
    ob = bpy.context.active_object

    # Get material
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
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
    bpy.context.object.name = material_name
