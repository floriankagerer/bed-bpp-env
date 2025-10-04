"""
This file contains argument parsing methods.
"""

import logging
import argparse
import utils

parser = argparse.ArgumentParser(description=__doc__, fromfile_prefix_chars="@")

__logger = logging.getLogger(__name__)

parsedArguments = {}
"""A dictionary that contains the parsed arguments"""


def addGroupToParser(title, description=""):
    """
    Adds a group to the global parser.

    Parameters.
    -----------
    title: str
        The title of the group
    description: str (default: "")
        The description of the added group.

    Returns.
    --------
    Returns a handle.
    """
    return parser.add_argument_group(title, description)


def parse():
    parsedArguments.update(vars(parser.parse_args()))

    if parsedArguments.get("debug", False):
        changeLoggingBasicConfiguration(logging.DEBUG)
    else:
        changeLoggingBasicConfiguration(logging.INFO)

    givenTask = parsedArguments.get("task", "None")
    # format the task in a general format, namely O3DBP-k-s
    if not (givenTask == "None"):
        taskComponents = givenTask.split("-")
        while len(taskComponents) < 3:
            taskComponents.append(1)
        if int(taskComponents[-1]) > int(taskComponents[-2]):
            # preview mustn't be greater than selection
            raise ValueError("The value of the preview k must not be smaller than the value of the selection s!")
        # O3DBP-k-s
        taskInGeneralFormat = "-".join([str(comp) for comp in taskComponents])
        parsedArguments["task"] = taskInGeneralFormat
        utils.updateUsedConfigurationFile()

    __logger.info(f"parsed the arguments {parsedArguments}")

    return parsedArguments


def changeLoggingBasicConfiguration(lowestlevel: int = logging.debug) -> None:
    """Changes the basic configuration of the `logging` module."""
    from utils.configuration import LOGGING_FILE as loggingfile

    logging.basicConfig(
        level=lowestlevel,
        format="%(asctime)s %(name)s %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(loggingfile), logging.StreamHandler()],
    )

    # set the levels that the logs are not polluted
    logging.getLogger("matplotlib").setLevel(logging.WARN)
    logging.getLogger("PIL").setLevel(logging.WARN)
