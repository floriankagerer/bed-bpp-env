"""
This file converts the result of the solver `josch/sisyphus`, which was developed for VMAC 2012, to a format that can be used by the BED-BPP infrastructure.

After the conversion, the result is appended to the file `"sisyphus_output.json"`.

This script should be run as main with `python3 packlistConverter.py --dir_solver <path/to/packlists/> --src_order <path/to/orders.json>`.

Note.
-----
It seems that the coordinates of the solver's output are not flb coordinates, but the coordinates on top of the package in the center.\n
(a) Information about the `orientation` value can be found in the file `arrange_spread2.py` in the directory `sisyphus-master`. The values of the solver $o_{solver} = o_{mypa\_solver} +1$\n
(b) Information about the `"z pack height"` can be found in the file `bruteforce3.py` in the directory `sisyphus-master`.
"""

import argparse
import ast
import glob
import json
import pathlib
import xml.etree.ElementTree as ET

import tqdm

OUTPUT_FNAME = "sisyphus_output.json"
"""The file that contains the results of sisyphus in JSON format."""

INT_STEP_CONV_FNAME = "interm_sisyphus_output.txt"
"""The file to which the conversion results of the xml files are appended."""


def __getOrderIDFromPacklistFile(filename: str) -> str:
    """Returns the order id of the packlist. The filename must be named like `packlist_001012345.xml`."""
    order_id = str(filename).split("packlist_")[-1]
    order_id = order_id.split(".xml")[0]
    return order_id


def __convXMLtoTXT(src_solver: str, src_order: dict, order_id: str) -> None:
    """
    Goes through the given `.xml`-file and converts its result to the bed-bpp_env format.

    Finally, the result is appended to a text file that can be used to generate the output file in JSON format.

    Parameters.
    -----------
    src_solver: str
        The output file of the solver with ending .xml.
    src_order: dict
        The order for which the packlist was generated.
    order_id: str
        The id of the order.
    """
    # load the solver's output
    solverPacklist = ET.parse(src_solver)
    root = solverPacklist.getroot()

    # get all packages in the packlist
    actions = []
    itemSequenceCounter = 1
    for child in root.iter("Package"):
        # itemID = child.findtext("Barcode")

        # convert the value of the orientation
        orientation = ast.literal_eval(child.findtext("Orientation")) - 1

        # obtain the item properties dictionary
        itemDescription = child.find("Article").findtext("Description")
        for item in list(src_order["item_sequence"].values()):
            if item["article"] == itemDescription:
                itemProps = item
                break
        # adapt the sequence value
        itemProps["sequence"] = itemSequenceCounter
        itemSequenceCounter += 1

        # obtain the LBB coordinates
        placePositions = child.find("PlacePosition")
        flbCoordinates = []
        for coord in ["X", "Y", "Z"]:
            flbCoordinates.append(ast.literal_eval(placePositions.findtext(coord)))
        # convert the coordinates to flb coordinates
        if orientation == 0:
            flbCoordinates[0] -= int(itemProps["length/mm"] / 2)
            flbCoordinates[1] -= int(itemProps["width/mm"] / 2)
        elif orientation == 1:
            flbCoordinates[0] -= int(itemProps["width/mm"] / 2)
            flbCoordinates[1] -= int(itemProps["length/mm"] / 2)
        else:
            raise ValueError(f"something went wrong with the orientation")
        flbCoordinates[-1] -= int(itemProps["height/mm"])

        # append action to all actions of this order
        actions.append({"flb_coordinates": flbCoordinates, "orientation": orientation, "item": itemProps.copy()})

    # append the new order to an existing json file
    with open(INT_STEP_CONV_FNAME, "a") as file:
        file.write(f"{order_id}:{actions}\n")


def __convertResultsToJSON() -> None:
    """Converts a text file which lines look like `key`:`value\\n` to a JSON file."""
    with open(INT_STEP_CONV_FNAME) as file:
        SOLVER_OUTPUT = file.readlines()

    outputJSON = {}
    for line in tqdm.tqdm(SOLVER_OUTPUT):
        orderID, actions = line.split(":", maxsplit=1)
        cleanActions = actions.rstrip("\n")

        outputJSON[orderID] = ast.literal_eval(cleanActions)

    with open(OUTPUT_FNAME, "w") as file:
        json.dump(outputJSON, file)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This file converts the result of the solver `josch/sisyphus`, which was developed for VMAC 2012, to a format that can be used for the bed-bpp_env infrastructure."
    )
    parser.add_argument(
        "--dir_solver",
        type=str,
        help="The directory that contains the packlists of the solver in xml format.",
        required=True,
    )
    parser.add_argument(
        "--src_order", type=str, help="The file that contains the order that is converted.", required=True
    )
    args = parser.parse_args()

    # load the orders of the benchmark data
    with open(args.src_order) as file:
        SRC_ORDER = json.load(file, parse_int=False)

    # get all packlists in directory and sort them ascending
    packlistFiles = glob.glob(f"{pathlib.Path(args.dir_solver).resolve().joinpath('packlist_*.xml')}")
    packlistFiles.sort()

    print(f"convert the packlists (XML -> TXT)")
    for fPacklist in tqdm.tqdm(packlistFiles):
        order_id = __getOrderIDFromPacklistFile(fPacklist)
        __convXMLtoTXT(src_solver=fPacklist, src_order=SRC_ORDER[order_id], order_id=order_id)

    # finally, create a JSON file from the lines in the TXT file
    print(f"convert the packlists (TXT -> JSON)")
    __convertResultsToJSON()
