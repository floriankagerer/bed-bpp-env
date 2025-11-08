from collections.abc import Callable
from enum import Enum

from bed_bpp_env.evaluation.blender.bpy_helpers.populators.euro_pallet import place_euro_pallet
from bed_bpp_env.evaluation.blender.bpy_helpers.populators.rollcontainer import place_rollcontainer

Position = tuple[float, float, float]
Rotation = tuple[float, float, float]


class Target(Enum):
    """Contains targets of the benchmarking dataset."""

    EURO_PALLET = "euro-pallet"
    ROLLCONTAINER = "rollcontainer"

    def get_camera_pose_in_blender(self) -> tuple[Position, Rotation]:
        """
        Returns the camera pose in Blender for the target.

        Returns:
            tuple[Position, Rotation]: The camera pose, i.e., the position and the rotation.
        """

        if self is Target.ROLLCONTAINER:
            camera_position = (2.3388, -2.3318, 2.1809)
            camera_rotation = (1.22872, -4.53789e-07, 0.642278)

        elif self is Target.EURO_PALLET:
            camera_position = (2.6788, -2.4603, 2.1692)
            camera_rotation = (1.22872, -4.53789e-07, 0.642278)

        else:
            raise NotImplementedError(f"No camera position defined for target '{self}'")

        return camera_position, camera_rotation

    def get_z_offset_for_floor_in_blender(self) -> float:
        """
        Returns the z-offset for the floor in the Blender scene.

        Returns:
            float: The z-offset.
        """
        if self is Target.ROLLCONTAINER:
            offset = -0.05 - 0.11 - 0.001

        elif self is Target.EURO_PALLET:
            offset = -0.144 - 0.002

        else:
            raise NotImplementedError(f"No z-offset for floor defined for target '{self}'")

        return offset

    def get_modelling_function_in_blender(self) -> Callable[[], None]:
        """
        Returns the function that adds the target to the Blender scene.

        Returns:
            Callable[[], None]: The function that adds the target to the Blender scene.
        """
        if self is Target.ROLLCONTAINER:
            modelling_function = place_rollcontainer

        elif self is Target.EURO_PALLET:
            modelling_function = place_euro_pallet

        else:
            raise NotImplementedError(f"No modelling function defined for target '{self}'")

        return modelling_function
