"""
This module contains utils such as a argument parser, a configuration parser and format converters. Note that this module must be called in every script in the beginning => it creates an output folder, stores the arguments parsed and loads the configuration.

### Accessible Variables
Variables that can be accessed by importing this package (with `utils.{VARNAME}`):\n
- ENTIRECONFIG: the complete config that is defined in the bed-bpp environment configuration file.\n
- OUTPUTDIRECTORY: the directory in which all results are stored.\n
- PARSEDARGUMENTS: dictionary that contains all arguments that were given when calling the script.

"""

import pathlib
import configparser
import utils.configuration
import utils.arguments_parser
import utils.sisyphus
import utils.xflp
import utils.o3dbpp_pct

# obtain the variables
OUTPUTDIRECTORY = utils.configuration.OUTPUTDIR
ENTIRECONFIG = utils.configuration.ENTIRECONFIG
PARSEDARGUMENTS = utils.arguments_parser.parsedArguments


def updateUsedConfigurationFile() -> None:
    """Updates the values of the preview k and selection s, according to the parsed task."""
    task = utils.arguments_parser.parsedArguments.get("task", "None")
    if not (task == "None"):
        config = configparser.ConfigParser()
        config.read(utils.configuration.USEDCONFIGURATIONFILE)

        _, k, s = task.split("-")
        config.set("environment", "preview", str(k))
        config.set("environment", "selection", str(s))

        with open(utils.configuration.USEDCONFIGURATIONFILE, "w") as file:
            config.write(file)


def getPathToExampleData() -> pathlib.Path:
    """Returns the path to the example data directory."""
    filePath = pathlib.Path(__file__)
    return filePath.parents[2].joinpath("example_data")
