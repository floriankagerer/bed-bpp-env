'''
This script generates for a given benchmark data file the corresponding database that stores the colors for the items within an order.
'''
import utils
import json
import logging
import pathlib
import tqdm

logger = logging.getLogger(__name__)


def generateColorDatabase(indataorders:pathlib.Path) -> None:
    '''
    Generates a json file for the given orders

    Parameters.
    -----------
    indataorders: pathlib.Path  
      The orders that are currently invesigated.  

    Output.
    -------
    >>> generateColorDatabase(...)
    {
        "00100001": {
            "article1_001": "color01",
            "article2_002": "color02",
            ...
        },
        "00100002": {
            ...
        }
    }
    '''
    colorsAvailable = utils.getPathToExampleData().parent.joinpath("code/visualization/colors/colors.json")

    # load input data orders and the color base
    with open(indataorders) as file:
        ORDERS_IN = json.load(file, parse_int=False)
    with open(colorsAvailable) as file:
        COLORBASE = json.load(file, parse_int=False)

    # tbd
    colorDatabase = {} # keys: order id, values: dict with article as key and color name as value
    logger.info(f"create the color database for {indataorders}.")
    for orderId, orderData in tqdm.tqdm(ORDERS_IN.items()):
        colorsInOrder = {}
        
        for item in orderData["item_sequence"].values():
            article = item["article"]
            if not(article in colorsInOrder.keys()):
                keyInColorbase = f"own_{str((len(colorsInOrder)%len(COLORBASE))+1).zfill(2)}"
                colorsInOrder[article] = keyInColorbase

        colorDatabase[orderId] = colorsInOrder

    # save the color db
    colordbFile = colorsAvailable.parent.joinpath(f"colordb_{indataorders.name}")
    logger.info(f"store the color database as {colordbFile}")
    with open(colordbFile, "w") as file:
        json.dump(colorDatabase, file)

