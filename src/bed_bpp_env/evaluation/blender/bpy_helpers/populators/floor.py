"""Module that contains functions to place the floor in Blender."""

from bed_bpp_env.evaluation.blender.bpy_helpers.data_model.rigid_body_type import RigidBodyType
import bpy  # type: ignore

from bed_bpp_env.evaluation.blender.target import Target

# TODO(florian): improve documentation, refactor material assignment


def place_floor(target: Target, size: tuple = (500, 500, 1)) -> None:
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
    z_offset_floor = target.get_z_offset_for_floor_in_blender()
    bpy.ops.transform.translate(value=(0, 0, z_offset_floor))

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
    bpy.context.object.rigid_body.type = RigidBodyType.PASSIVE
    bpy.context.object.name = "bottom"
