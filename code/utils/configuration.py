'''
This module loads the configurations as given in `bed-bpp_env.conf` (`ENTIRECONFIG`), creates an output folder where all simulation results are stored (`OUTPUTDIR`), and defines the configuration of the `logging` module. In order to make the simulations reproducable, the loaded configuration file is copied to the generated output folder.

Note.
-----
Access the variables via the module `utils`.
'''
import logging
__logger = logging.getLogger(__name__)
import pathlib
import configparser
import datetime
import shutil


# define the names of the different files/folders
fnameConfiguration = "bed-bpp_env.conf"
currentOutputfname = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
fnameLogging = "logs.log"

# create the path to the configuration file
dirFile = pathlib.Path(__file__).parent.resolve()
dirConfigFile = dirFile.parent.resolve() # go one level/folder up
configFile = pathlib.Path.joinpath(dirConfigFile, fnameConfiguration)

# create the outputfolder
dirOutput = dirFile.parents[1].resolve() # go two levels up
dirOutput = pathlib.Path.joinpath(dirOutput, f"output/{datetime.datetime.now().strftime('%Y-%m-%d')}")
OUTPUTDIR = pathlib.Path.joinpath(dirOutput, currentOutputfname)
OUTPUTDIR.mkdir(parents=True, exist_ok=True)

# configure the logging module
LOGGING_FILE = pathlib.Path.joinpath(OUTPUTDIR, fnameLogging)

# read the configuration from the previously defined directory
ENTIRECONFIG = configparser.ConfigParser()
__logger.info(f"loaded the configuration from {configFile}")
ENTIRECONFIG.read(configFile)


# copy the used configuration file
shutil.copy(configFile, OUTPUTDIR)
__logger.info(f"copied the configuration to {OUTPUTDIR}")
USEDCONFIGURATIONFILE = pathlib.Path.joinpath(OUTPUTDIR, fnameConfiguration)

if __name__ == "__main__":
    pass