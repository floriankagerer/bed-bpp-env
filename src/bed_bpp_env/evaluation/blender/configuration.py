"""Responsible for the configuration of Blender in this package."""

import logging
from pathlib import Path
from platform import platform
from typing import Optional

logger = logging.getLogger(__name__)


def blender_path_in_configuration(evaluation_configuration: dict) -> Optional[str]:
    """
    Reads the blender path from the configuration.

    Args:
        evaluation_configuration (dict):

    Returns:
        Optional[str]:

    """
    blender_path = evaluation_configuration["blenderpath"]
    if blender_path == "":
        return None
    else:
        logger.info(f"Use Blender path from configuration: '{blender_path}'")
        return blender_path


def retrieve_blender_path(evaluation_configuration: dict) -> Path:
    """
    Returns the path to Blender, based on the used operating system.

    Args:
        evaluation_configuration (dict):

    Returns:
        str: The

    """
    configured_blender_path = blender_path_in_configuration(evaluation_configuration)

    if configured_blender_path is None:
        # use default paths
        used_platform = platform()
        if "macOS" in used_platform:
            blender_path = Path("/Applications/Blender.app/Contents/MacOS/Blender")
        elif "Linux" in used_platform:
            blender_path = Path("/snap/blender/current/blender")
        else:
            raise ValueError(
                f"platform {used_platform} is currently not implemented > set blenderpath in bed-bpp_env.conf"
            )

    else:
        # check whether file exists
        blender_path = Path(configured_blender_path)
        if not blender_path.exists():
            raise FileNotFoundError(f"Could not find Blender as configured: '{configured_blender_path}'")

    return blender_path
