"""
This module provides classes to visualize the packing process.
"""

import json
import pathlib

from bed_bpp_env.utils import OUTPUTDIRECTORY as UTILS_OUTPUTDIRECTORY
from bed_bpp_env.utils import PARSEDARGUMENTS
from bed_bpp_env.visualization.colors import generate_color_database


OUTPUTDIRECTORY = pathlib.Path.joinpath(UTILS_OUTPUTDIRECTORY, "vis")
OUTPUTDIRECTORY.mkdir(parents=True, exist_ok=True)

# load the correct color database
usedData = PARSEDARGUMENTS.get("data")
if isinstance(usedData, str):
    usedData = pathlib.Path(usedData)
if not (usedData is None):
    colorDBFilename = pathlib.Path(__file__).parent.resolve().joinpath(f"colors/colordb_{usedData.name}")
    if not (colorDBFilename.exists()):
        generate_color_database.generateColorDatabase(usedData)
    with open(colorDBFilename) as file:
        COLOR_DATABASE = json.load(file, parse_int=False)
