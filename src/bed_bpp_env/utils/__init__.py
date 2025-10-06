"""
This module contains utils such as a argument parser, a configuration parser and format converters. Note that this module must be called in every script in the beginning => it creates an output folder, stores the arguments parsed and loads the configuration.

### Accessible Variables
Variables that can be accessed by importing this package (with `utils.{VARNAME}`):\n
- ENTIRECONFIG: the complete config that is defined in the bed-bpp environment configuration file.\n
- OUTPUTDIRECTORY: the directory in which all results are stored.\n
- PARSEDARGUMENTS: dictionary that contains all arguments that were given when calling the script.

"""

import pathlib
from bed_bpp_env.utils.configuration import OUTPUTDIR, ENTIRECONFIG, USEDCONFIGURATIONFILE
import bed_bpp_env.utils.arguments_parser as arguments_parser

OUTPUTDIRECTORY = OUTPUTDIR
ENTIRECONFIG = ENTIRECONFIG
PARSEDARGUMENTS = arguments_parser.parsedArguments


def getPathToExampleData() -> pathlib.Path:
    """Returns the path to the example data directory."""
    filePath = pathlib.Path(__file__)
    return filePath.parents[3].joinpath("example_data")
