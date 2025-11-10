"""
This module loads the configurations as given in `bed-bpp_env.conf` (`ENTIRECONFIG`), creates an output folder where all simulation results are stored (`OUTPUTDIR`), and defines the configuration of the `logging` module. In order to make the simulations reproducable, the loaded configuration file is copied to the generated output folder.

Note.
-----
Access the variables via the module `utils`.
"""

import configparser
import datetime
import logging
import shutil
from pathlib import Path

__logger = logging.getLogger(__name__)

# define the names of the different files/folders
FILENAME_CONFIGURATION = "bed-bpp_env.conf"
"""The filename of the configuration file."""
currentOutputfname = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
fnameLogging = "logs.log"

# create the path to the configuration file
dirFile = Path(__file__).parent.resolve()
dirConfigFile = dirFile.parent.resolve()  # go one level/folder up
configFile = Path.joinpath(dirConfigFile, FILENAME_CONFIGURATION)

# create the outputfolder
dirOutput = dirFile.parents[2].resolve()  # go three levels up
dirOutput = Path.joinpath(dirOutput, f"output/{datetime.datetime.now().strftime('%Y-%m-%d')}")
OUTPUTDIR = Path.joinpath(dirOutput, currentOutputfname)
OUTPUTDIR.mkdir(parents=True, exist_ok=True)

# configure the logging module
LOGGING_FILE = Path.joinpath(OUTPUTDIR, fnameLogging)

# read the configuration from the previously defined directory
ENTIRECONFIG = configparser.ConfigParser()
__logger.info(f"loaded the configuration from {configFile}")
ENTIRECONFIG.read(configFile)


# copy the used configuration file
shutil.copy(configFile, OUTPUTDIR)
__logger.info(f"copied the configuration to {OUTPUTDIR}")
USEDCONFIGURATIONFILE = Path.joinpath(OUTPUTDIR, FILENAME_CONFIGURATION)


def copy_configuration_file_to_output_directory(output_dir: Path) -> Path:
    """
    Copies the configuration file to the output directory.

    Args:
        output_directory (Path): The output directory.

    Returns:
        Path: The path to the copied configuration file.
    """
    config_file_path = Path(__file__).parents[1] / FILENAME_CONFIGURATION

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    copied_config_file_path = output_dir / FILENAME_CONFIGURATION
    shutil.copy(config_file_path, output_dir)

    return copied_config_file_path
