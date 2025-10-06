"""
This scripts convert the results of the solver `xflp` of Holger Schneider to a format of the bed-bpp environment. It saves two files:

(1) the original output of the solver and
(2) the output of the solver where the items are sorted with ascending z value of the FLB coordinates.

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

import yaml


def __convertToYamlStructure(singleOrderActions: dict) -> dict:
    """
    Converts the dictionary of a single order to a dictionary that can be saved correctly to a `.yaml`-file.

    Parameters.
    -----------
    singleOrderActions: dict
        The action of an order that are converted.

    Returns.
    --------
    convertedActions: dict
        The actions converted such that the format of the stored `.yaml`-file is identical to a unittest order's format.
    """
    yamlActions = []
    for allActions in singleOrderActions.values():
        for action in allActions:
            yamlActions.append({f"action{len(yamlActions)}": action})

    orderID = list(singleOrderActions.keys())[0]
    return {orderID: yamlActions}


def __getItemPropertiesOfArticle(ORDER: dict, line: str) -> dict:
    """
    Returns the properties of the item that is given in `line`.

    Parameters.
    -----------
    ORDER: dict
        The order for which the actions are converted.
    line: str
        A line of the output of the Java solver of hschneid.

    Returns.
    --------
    props: dict
        The item's properties
    """
    # get the article properties
    article, _ = line.split(" LOAD ")
    itemPropsFound = False
    i = 1
    while not (itemPropsFound):
        props = ORDER["item_sequence"][str(i)]

        if props["article"] == article:
            itemPropsFound = True
        else:
            i += 1

    for key, val in props.items():
        if "/mm" in key:
            props[key] = int(val)

    return props


def __getFLBCoordinatesAndOrientation(itemProps: dict, line: str) -> typing.Tuple:
    """
    Returns the FLB coordinates of the item specified in `line` and its orientation.

    Parameters.
    -----------
    ORDER: dict
        The order for which the actions are converted.
    line: str
        A line of the output of the Java solver of hschneid.

    Returns.
    --------
    A tuple with the following elements:
    lbbCoordinates: list
        The lbb coordinates of the item.
    orientation: int
        The orientation of the item.
    """
    sizeAndTarget = line.split("| ")[-1]

    lenwidheight, target = sizeAndTarget.split(" : ")
    lenwidheight = lenwidheight.rstrip()
    target = target.rstrip()
    length, width, height = lenwidheight.split(" ")
    l, w = ast.literal_eval(length), ast.literal_eval(width)
    target = target.rstrip()
    x, y, z = target.split(" ")
    x = ast.literal_eval(x)
    y = ast.literal_eval(y)
    z = ast.literal_eval(z)

    # get the orientation of the item
    if (l == itemProps["length/mm"]) and (w == itemProps["width/mm"]):
        orientation = 0
    elif (l == itemProps["width/mm"]) and (w == itemProps["length/mm"]):
        orientation = 1
    else:
        logger.warning("orientation - something went wrong!")

    return [x, y, z], orientation


def obtainActionFromLogfileLine(ORDER: dict, line: str) -> dict:
    """
    Obtains a dictionary that contains a palletizing action.

    Parameters.
    -----------
    ORDER: dict
        The order for which the actions are converted.
    line: str
        A line of the output of the Java solver of hschneid.

    Returns.
    --------
    action: dict
        The converted action.
    """
    line = line.rstrip("\n")

    itemProps = __getItemPropertiesOfArticle(ORDER, line)
    lbbCoordinates, orientation = __getFLBCoordinatesAndOrientation(itemProps, line)

    return {"item": itemProps.copy(), "flb_coordinates": lbbCoordinates, "orientation": orientation}


def convertToActionDictionary(src_order: dict, orderID: str) -> dict:
    """
    Converts the action of the specified order from the `.txt`-file of the Java solver to the format of the bed-bpp environment.

    Parameters.
    -----------
    orderID: str
        The id of the order.

    Returns.
    --------
    orderActions: dict
        A dictionary that holds the order ids as keys and the corresponding actions as values.
    """
    ORDER = src_order[orderID]
    orderActions = []

    lineNrOfOrder = SRC_SOLVER.index(f"order id:{orderID}\n")
    endLineNrOfOrder = SRC_SOLVER.index(f"====================\n", lineNrOfOrder)

    for line in SRC_SOLVER[lineNrOfOrder + 1 : endLineNrOfOrder]:
        if (">>>" in line[:4]) or ("---" in line[:4]):
            pass

        elif "not placed items" in line:
            # check how many items were not placed
            text, amountNotPlaced = line.split("=")
            amountNotPlaced = ast.literal_eval(amountNotPlaced.rstrip("\n"))
            if amountNotPlaced:
                logger.warning(f"order {orderID} - have {amountNotPlaced} items that are *not* placed")

        else:
            # have an item
            action = obtainActionFromLogfileLine(ORDER, line)
            action["item"]["sequence"] = len(orderActions) + 1
            orderActions.append(action.copy())

    return {orderID: orderActions}


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    """
    Main of the converter.
    """
    loggingfile = "logs.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(loggingfile), logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Possible arguments for the results converter Java => Python.")
    parser.add_argument(
        "--src_solver",
        type=str,
        default="java_output.txt",
        help="The source file that is converted to the needed format in Python.",
    )
    parser.add_argument("--src_order", type=str, help="The order data that was used to create the solver output..")
    parser.add_argument(
        "--dest",
        type=str,
        default="xflp_output.json",
        help="The file that holds the actions in the needed Python format.",
    )
    parser.add_argument(
        "--yaml",
        type=str,
        default="None",
        help="Defines the order that is converted to `.yaml`. Note that this can only be one order.",
    )
    args = parser.parse_args()

    # load the src files
    with open(args.src_order) as file:
        SRC_ORDER = json.load(file, parse_int=False)
    with open(args.src_solver) as file:
        SRC_SOLVER = file.readlines()

    # the dictionary that is saved
    actionDictionary = {}

    if args.yaml == "None":
        # convert all orders
        orderIDs = []
        for line in SRC_SOLVER:
            if "order id" in line:
                orderID = line.split(":")[-1]
                orderID = orderID.rstrip("\n")
                orderIDs.append(orderID)

        orderIDs.sort(key=int)

        for orderID in orderIDs:
            actionDictionary.update(convertToActionDictionary(src_order=SRC_ORDER, orderID=orderID))

    else:
        # convert single order
        orderID = args.yaml
        actionDictionary.update(convertToActionDictionary(src_order=SRC_ORDER, orderID=orderID))
        actionsYAML = __convertToYamlStructure(actionDictionary)
        with open(f"{orderID}_output.yaml", "w") as file:
            yaml.dump(actionsYAML, file)

    # save the dictionary
    insertIdx = args.dest.find(".json")
    fname = args.dest[:insertIdx] + "_orig-hschneid" + args.dest[insertIdx:]
    with open(fname, "w") as file:
        json.dump(actionDictionary, file)

    for actionsList in actionDictionary.values():
        actionsList.sort(key=lambda x: x["flb_coordinates"][-1])

    # save the dictionary
    insertIdx = args.dest.find(".json")
    fname = args.dest[:insertIdx] + "_asc-z" + args.dest[insertIdx:]
    with open(fname, "w") as file:
        json.dump(actionDictionary, file)
