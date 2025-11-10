"""
Converts the results of `alexfrom0815/Online-3D-BPP-PCT` to the format that is used in BED-BPP.

Procedure.
----------
(1) Load the data from the .txt file.
(2) For each order
    (a) convert the order to the pre-defined json format
(3) Save all orders in a new .json file.
"""

import argparse
import ast
import json
import logging
import typing

import numpy as np
from tqdm import tqdm

from bed_bpp_env.utils import OUTPUTDIRECTORY

logger = logging.getLogger(__name__)
loggingfile = OUTPUTDIRECTORY.joinpath("converter_logs.log")
logger.addHandler(logging.FileHandler(loggingfile))


FACTOR_X, FACTOR_Y, FACTOR_Z = 10, 10, 10
DEFAULT_ITEM_WEIGHT = 9.99


def mergeResultsForDifferentTargets(order: dict, resultssolver: dict) -> dict:
    """

    Parameters.
    -----------
    order: dict
        tbd
    resultssolvers: dict
        TBD

    Returns.
    --------
    mergedResults: dict
        tbd

    Examples.
    ---------
    >>> resultssolver
    {
        "rollcontainer": ...,
        "euro-pallet": ...
    }

    >>> mergedResults
    {
        "00100001": pass # LINES that are important
    }
    """
    mergedResults = {}

    for i, idAndInformation in enumerate(order.items()):
        orderID, information = idAndInformation
        target = information["properties"]["target"]

        srcIndices = resultssolver[target]["order_information"][orderID]
        startIdx, endIdx = srcIndices.get("start"), srcIndices.get("end")

        data = resultssolver[target]["data"]

        mergedResults[orderID] = data[startIdx:endIdx]

    return mergedResults


def getItemPropertiesFromSize(orderitemsequence: dict, itemsize: list, iteratorinseq: int) -> dict:
    length, width, height = itemsize
    possibleItems = {}
    orientations = {}
    toleranceValue = 10

    for item in orderitemsequence.values():
        if (
            abs(item["length/mm"] - length) <= toleranceValue
            and abs(item["width/mm"] - width) <= toleranceValue
            and abs(item["height/mm"] - height) <= toleranceValue
            and not (item["article"] in possibleItems.keys())
        ):
            possibleItems[item["article"]] = item
            orientations[item["article"]] = 0
        elif (
            abs(item["length/mm"] - width) <= toleranceValue
            and abs(item["width/mm"] - length) <= toleranceValue
            and abs(item["height/mm"] - height) <= toleranceValue
            and not (item["article"] in possibleItems.keys())
        ):
            possibleItems[item["article"]] = item
            orientations[item["article"]] = 1

    if len(possibleItems) > 1:
        logger.warning(f"no unique matching by size!")
        minDistanceToIterator = np.inf
        possibleItemChoice = None
        for item in possibleItems.values():
            itemSeqNumber = item["sequence"]
            deltaToIterator = abs(itemSeqNumber - iteratorinseq)
            if deltaToIterator < minDistanceToIterator:
                minDistanceToIterator = deltaToIterator
                possibleItemChoice = item

        itemOrientation = orientations[item["article"]]
        logger.info(f"selected {possibleItemChoice}")

    else:
        possibleItemChoice = possibleItems[list(possibleItems.keys())[0]]
        itemOrientation = orientations[list(orientations.keys())[0]]

    itemProps = possibleItemChoice
    return itemProps, itemOrientation


def __prepareSRC_SOLVER(src_solver: list) -> typing.Tuple:
    """
    Prepares the solver's source file for the conversion.

    Parameters.
    -----------
    src_solver:list
        The lines of the txt file of the solver's output.

    Returns.
    --------
    cleaned_src_solver:list
        The cleaned src_solver file that does not contain tailed "\\n".
    order_information:dict
        The keys are the order ids and the values are dictionaries that contain the start index and the end index of the order in the txt file of the solver.
    """
    cleaned_src_solver = []
    order_information = {}

    packingPlanIndices = []
    for lineNr, line in enumerate(src_solver):
        # remove \n from end of line
        cleaned_src_solver.append(line.rstrip("\n"))
        # find the packing plan indices
        if "PACKING PLAN" in line:
            packingPlanIndices.append(lineNr)
    packingPlanIndices.append(len(src_solver))

    while len(packingPlanIndices) > 1:
        startIdx, endIdx = packingPlanIndices.pop(0) + 1, packingPlanIndices[0]

        orderKey = "001" + str(len(order_information) + 1).zfill(5)

        order_information[orderKey] = {"start": startIdx, "end": endIdx}

    return cleaned_src_solver, order_information


def createOrderDataFromSolution() -> None:
    """
    This method converts the output of the Online-3D-BPP-DRL solver by alexfrom0815 to the known benchmark data format.
    """
    pass


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    """
    Main of the converter.
    """
    from bed_bpp_env.utils import getPathToExampleData
    from bed_bpp_env.utils.o3dbpp_pct import DEFAULT_FILENAME_CONVERTED_OUTPUT

    if not OUTPUTDIRECTORY.exists():
        OUTPUTDIRECTORY.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(
        description="Possible arguments for the results converter Online-3D-BPP-PCT => MyPa format."
    )
    parser.add_argument(
        "--src_solver", nargs="+", help="The list of source files that is converted to the needed format in Python."
    )
    parser.add_argument(
        "--src_order",
        type=str,
        default=getPathToExampleData().joinpath("benchmark_data/bed-bpp_v1.json"),
        help="The order data that was used to create the solver output..",
    )
    parser.add_argument(
        "--dest",
        type=str,
        default=DEFAULT_FILENAME_CONVERTED_OUTPUT,
        help="The location where the converted output is stored.",
    )
    args = parser.parse_args()

    with open(args.src_order) as file:
        SRC_ORDER = json.load(file, parse_int=False)

    print(args.src_solver, type(args.src_solver))

    resultsSolver = {}
    if isinstance(args.src_solver, list):
        for fNameResults in args.src_solver:
            with open(fNameResults) as file:
                dataSolver = file.readlines()

            cleanedData, orderInformation = __prepareSRC_SOLVER(dataSolver)

            if "rollcontainer" in str(fNameResults):
                resultsSolver["rollcontainer"] = {"data": cleanedData, "order_information": orderInformation}
            elif "euro-pallet" in str(fNameResults):
                resultsSolver["euro-pallet"] = {"data": cleanedData, "order_information": orderInformation}
            else:
                raise ValueError("this target is not implemented now")

        mergedResults = mergeResultsForDifferentTargets(SRC_ORDER, resultsSolver)

    else:
        with open(args.src_solver) as file:
            SRC_SOLVER = file.readlines()
        # prepare data
        CLEANED_SRC_SOLVER, orderInformation = __prepareSRC_SOLVER(SRC_SOLVER)

    # print(f"merged results: {mergedResults}")

    actionDictionary = {}
    # converts the solution to an order that can be parsed to different algorithms
    inputDataOrders = {}

    for orderKey, srcIndices in orderInformation.items():
        startIdx, endIdx = srcIndices.get("start"), srcIndices.get("end")

        actionDictionary[orderKey] = []
        inputDataOrders[orderKey] = {}
        inputDataOrders[orderKey]["properties"] = {
            "target": "euro-pallet",
            "id": orderKey,
            "order_nr": orderKey,
            "type": "generic",
        }
        inputDataOrders[orderKey]["item_sequence"] = {}

        # create the packing plan in json format
        for i, line in tqdm(enumerate(mergedResults[orderKey])):
            # for line in CLEANED_SRC_SOLVER[startIdx:endIdx]:
            searchC = "=("
            sizeIdxStart = line.find(searchC) + len(searchC)
            sizeIdxEnd = line.find(")", sizeIdxStart)
            lbbIdxStart = line.find(searchC, sizeIdxEnd) + len(searchC)
            lbbIdxEnd = line.find(")", lbbIdxStart)

            sizeStr = line[sizeIdxStart:sizeIdxEnd]
            sizeX, sizeY, sizeZ = sizeStr.split(",")
            sizeX, sizeY, sizeZ = ast.literal_eval(sizeX), ast.literal_eval(sizeY), ast.literal_eval(sizeZ)

            lbbCoordStr = line[lbbIdxStart:lbbIdxEnd]
            lbbX, lbbY, lbbZ = lbbCoordStr.split(",")
            lbbX, lbbY, lbbZ = ast.literal_eval(lbbX), ast.literal_eval(lbbY), ast.literal_eval(lbbZ)

            # print(f"size: {sizeX, sizeY, sizeZ} | lbb: {lbbX, lbbY, lbbZ}")

            itemProps, orientation = getItemPropertiesFromSize(
                SRC_ORDER[orderKey]["item_sequence"], [FACTOR_X * sizeX, FACTOR_Y * sizeY, FACTOR_Z * sizeZ], i
            )

            itemProperties = {
                "length/mm": FACTOR_X * sizeX,
                "width/mm": FACTOR_Y * sizeY,
                "height/mm": FACTOR_Z * sizeZ,
                "weight/kg": DEFAULT_ITEM_WEIGHT,
                "id": f"c{sizeX}{sizeY}{sizeZ}",
                "article": f"article_{sizeX}{sizeY}{sizeZ}",
                "product_group": "pg_1",
                "sequence": len(actionDictionary[orderKey]) + 1,
            }

            action = {
                "item": itemProps,
                "flb_coordinates": [FACTOR_X * lbbX, FACTOR_Y * lbbY, FACTOR_Z * lbbZ],
                "orientation": orientation,
            }

            actionDictionary[orderKey].append(action)

            # add item to item sequence
            itemPropertieswrtOrientation = itemProperties.copy()
            if not (itemPropertieswrtOrientation.get("length/mm") >= itemPropertieswrtOrientation.get("width/mm")):
                # change length and width since length must be geq width
                length, width = (
                    itemPropertieswrtOrientation.get("length/mm"),
                    itemPropertieswrtOrientation.get("width/mm"),
                )
                itemPropertieswrtOrientation["length/mm"] = width
                itemPropertieswrtOrientation["width/mm"] = length

            inputDataOrders[orderKey]["item_sequence"][str(len(inputDataOrders[orderKey]["item_sequence"]) + 1)] = (
                itemProperties
            )

    # save the dictionary
    print(f"save file in {args.dest}")
    with open(args.dest, "w") as file:
        json.dump(actionDictionary, file)
