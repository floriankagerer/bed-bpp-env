"""Module that contains functions to place a Euro-pallet in Blender."""

import bpy  # type: ignore

from bed_bpp_env.evaluation.blender.bpy_object_properties import set_material_and_enable_rigid_body


def _add_euro_pallet_part(position: tuple[float, float, float], size: tuple[float, float, float]) -> None:
    """Adds the part of a Euro-pallet to the scene in Blender."""
    offset_x, offset_y, offset_z = 0, 0, -0.144 - 0.001
    shifted_position = [position[0] + offset_x, position[1] + offset_y, position[2] + size[2] / 2 + offset_z]
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        calc_uvs=True,
        enter_editmode=False,
        align="WORLD",
        location=list(shifted_position),
        rotation=(0.0, 0.0, 0.0),
        scale=size,
    )
    set_material_and_enable_rigid_body("pal_part")


def place_euro_pallet() -> None:
    """Adds a Euro-pallet to the Blender bpy contect scene."""
    # Lowest layer
    positions = [(0 + 0.6, 0 + 0.1 / 2, 0), (0 + 0.6, 0.4, 0), (0 + 0.6, 0.8 - 0.1 / 2, 0)]
    sizes = [(1.2, 0.1, 0.022), (1.2, 0.145, 0.022), (1.2, 0.1, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # Lower middle layer
    positions = [
        (0 + 0.145 / 2, 0 + 0.1 / 2, 0.022),
        (0 + 0.145 / 2, 0.4, 0.022),
        (0 + 0.145 / 2, 0.8 - 0.1 / 2, 0.022),
    ]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    positions = [
        (1.2 - 0.145 / 2, 0 + 0.1 / 2, 0.022),
        (1.2 - 0.145 / 2, 0.4, 0.022),
        (1.2 - 0.145 / 2, 0.8 - 0.1 / 2, 0.022),
    ]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    positions = [(0.6, 0 + 0.1 / 2, 0.022), (0.6, 0.4, 0.022), (0.6, 0.8 - 0.1 / 2, 0.022)]
    sizes = [(0.145, 0.1, 0.078), (0.145, 0.145, 0.078), (0.145, 0.1, 0.078)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # "Balken" quer
    positions = [(0 + 0.145 / 2, 0.4, 0.1), (0.6, 0.4, 0.1), (1.2 - 0.145 / 2, 0.4, 0.1)]
    sizes = [(0.145, 0.8, 0.022), (0.145, 0.8, 0.022), (0.145, 0.8, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # längsbalken ganz oben breit
    positions = [(0.6, 0 + 0.145 / 2, 0.122), (0.6, 0.4, 0.122), (0.6, 0.8 - 0.145 / 2, 0.122)]
    sizes = [(1.2, 0.145, 0.022), (1.2, 0.145, 0.022), (1.2, 0.145, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)

    # längsbalken ganz oben schmal
    positions = [(0.6, 0.4 - 0.145 / 2 - 0.04 - 0.1 / 2, 0.122), (0.6, 0.4 + 0.145 / 2 + 0.04 + 0.1 / 2, 0.122)]
    sizes = [(1.2, 0.1, 0.022), (1.2, 0.1, 0.022)]
    for pos, size in zip(positions, sizes):
        _add_euro_pallet_part(pos, size)
