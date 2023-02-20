'''
This module provides classes to visualize the packing process.
'''
import json
import pathlib
import utils

import visualization.colors.generate_color_database

OUTPUTDIRECTORY = pathlib.Path.joinpath(utils.OUTPUTDIRECTORY, "vis")
OUTPUTDIRECTORY.mkdir(parents=True, exist_ok=True)

# load the correct color database
usedData = utils.PARSEDARGUMENTS.get("data")
if isinstance(usedData, str):
    usedData = pathlib.Path(usedData)
if not(usedData is None):
    colorDBFilename = pathlib.Path(__file__).parent.resolve().joinpath(f"colors/colordb_{usedData.name}")
    if not(colorDBFilename.exists()):
        visualization.colors.generate_color_database.generateColorDatabase(usedData)
    with open(colorDBFilename) as file:
        COLOR_DATABASE = json.load(file, parse_int=False)



from visualization.Visualization import Visualization
from visualization.PalletizingEnvironmentVisualization import PalletizingEnvironmentVisualization
from visualization.Video import Video
