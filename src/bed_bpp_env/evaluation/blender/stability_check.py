"""Module to evaluate the stability of a packing plan with Blender."""

from pathlib import Path
import subprocess

from bed_bpp_env.data_model.order import Order
from bed_bpp_env.data_model.packing_plan import PackingPlan

TEMPLATE_BLEND_PATH = Path(__file__).parent / "template.blend"
"""The path to the template Blender file."""

SCENE_CREATION_SCRIPT_PATH = Path(__file__).parent / "scene_creation.py"
"""The path to the script that generates the Blender scene."""


def _build_stability_check_cmd(
    blender_path: Path,
    blender_template: Path,
    scene_generation_script: Path,
    order: Order,
    packing_plan: PackingPlan,
    output_dir: Path,
    colors: dict,
    run_blender_in_background: bool = True,
    render_scene: bool = False,
) -> list[str]:
    """
    Builds the command to run a stability check with Blender.

    Args:
        blender_path (Path): The path to Blender.
        blender_template (Path): The path to the template .blend file.
        scene_generation_script (Path): The path to the .py file that is used to generate the scene.
        order (Order): The order for that the packing plan was generated.
        packing_plan (PackingPlan): The packing plan that is evaluated.
        output_dir (Path): The directory the output is written to.
        colors (dict): The colors that are used for coloring the items.
        run_blender_in_background (bool): Indicates whether Blender is run in background. Defaults to `True`.
        render_scene (bool): Indicates whether the scene is rendered. Defaults to `False`.

    Returns:
        list[str]: The command that is used to run the Blender stability check.
    """
    serialized_actions = [action.to_dict() for action in packing_plan.actions]

    cmd = [
        blender_path.as_posix(),
        # here would be the flag that indicates whether Blender is run in background
        blender_template.as_posix(),
        "--python",
        scene_generation_script.as_posix(),
        "--python-use-system-env",
        "--",
        "order_number",
        packing_plan.id,
        "output_dir",
        output_dir.as_posix(),
        "render",
        str(render_scene),
        "order_packing_plan",
        str(serialized_actions),
        "order",
        # TODO(florian): replace with str(order.to_dict())
        str(order),
        "order_colors",
        str(colors),
    ]

    if run_blender_in_background:
        cmd.insert(1, "-b")

    return cmd


def run_blender_stability_check_in_subprocess(
    blender_path: Path,
    order: Order,
    packing_plan: PackingPlan,
    output_dir: Path,
    colors: dict,
    run_blender_in_background: bool = True,
    render_scene: bool = False,
) -> None:
    """
    Runs a Blender stability check in a subprocess.

    Args:
        blender_path (Path): The path to Blender.
        order (Order): The order for that the packing plan was generated.
        packing_plan (PackingPlan): The packing plan that is evaluated.
        output_dir (Path): The directory the output is written to.
        colors (dict): The colors that are used for coloring the items.
        run_blender_in_background (bool): Indicates whether Blender is run in background. Defaults to `True`.
        render_scene (bool): Indicates whether the scene is rendered. Defaults to `False`.
    """
    cmd = _build_stability_check_cmd(
        blender_path=blender_path,
        blender_template=TEMPLATE_BLEND_PATH,
        scene_generation_script=SCENE_CREATION_SCRIPT_PATH,
        packing_plan=packing_plan,
        order=order,
        output_dir=output_dir,
        colors=colors,
        run_blender_in_background=run_blender_in_background,
        render_scene=render_scene,
    )
    subprocess.run(cmd, shell=False)
