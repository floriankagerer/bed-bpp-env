"""
This file converts an order of the benchmark dataset to a fromat that can be used by the solver `josch/sisyphus`. This solver was developed for the VMAC 2012.

After the conversion, the result is saved in `order_<order_id>.xml`.

This file can either be run as main with `python3 orderConverter.py --src_order <orders.json> --order_id <order_id>`, or called by `utils.sisyphus.orderConverter.converOrder(src_order=<orders.json>, -order_id=<order_id>)`.
"""

import argparse
import json
import xml.etree.ElementTree as ET

TARGET_MAX_LOAD_HEIGHT = 3000
TARGET_MAX_LOAD_WEIGHT = 166667


def __indent(elem, level=0):
    """Creates the indent of the xml-file-"""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            __indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def convertOrder(src_order: str, order_id: str) -> None:
    """
    Converts the order, which is specified by the given id, to an `xml`-file that has the format that is needed by the solver `josch/sisyphus`. This solver was developed for VMAC 2012.

    Finally, the converted order is saved as `order_<order_id>.xml`.

    Parameters.
    -----------
    src_order: str
        The json file that contains the order that is converted to an `.xml`-file for the solver.
    order_id: str
        The id of the order.
    """
    with open(src_order) as file:
        SRC_ORDER = json.load(file, parse_int=False)

    ORDERID = order_id
    if ORDERID in SRC_ORDER.keys():
        ORDER = SRC_ORDER[ORDERID]
    else:
        raise ValueError(f"order with id {ORDERID} is not in file {src_order}")

    # gather the information for the xml tree
    firstItem = None
    orderlines = []
    orderline = {}
    for item in list(ORDER["item_sequence"].values()):
        if firstItem is None:
            firstItem = item
            orderline["properties"] = item.copy()
            itemCount = 0
            barcodes = []
        if item["id"] == firstItem["id"]:
            # create orderline
            itemCount += 1
            barcodes.append(f"{item['id']}_{item['sequence']}")
        else:
            orderline["barcodes"] = barcodes
            orderlines.append(orderline.copy())

            firstItem = item
            orderline["properties"] = item.copy()
            itemCount = 0
            barcodes = [f"{item['id']}_{item['sequence']}"]
    # append the last barcodes and orderline
    orderline["barcodes"] = barcodes
    orderlines.append(orderline)

    BENDATA_ORDERLINES = orderlines

    palletizingTarget = ORDER["properties"]["target"]
    if palletizingTarget == "rollcontainer":
        targetLength, targetWidth = 800, 700
    elif palletizingTarget == "euro-pallet":
        targetLength, targetWidth = 1200, 800
    else:
        raise ValueError(f"unknown value of palletizing target -> {palletizingTarget}")

    # create the tree for the xml file
    root = ET.Element("Message", {"index": "1"})
    # Message > PalletInit : Pallets
    palletInit = ET.SubElement(root, "PalletInit")
    pallets = ET.SubElement(palletInit, "Pallets")
    # Message > PalletInit : Pallets > Pallet
    pallet = ET.SubElement(pallets, "Pallet")
    ET.SubElement(pallet, "PalletNumber").text = "1"
    ET.SubElement(pallet, "Description").text = palletizingTarget
    # Message > PalletInit : Pallets > Pallet : Dimensions
    dimensions = ET.SubElement(pallet, "Dimensions")
    ET.SubElement(dimensions, "Length").text = str(targetLength)
    ET.SubElement(dimensions, "Width").text = str(targetWidth)
    ET.SubElement(dimensions, "MaxLoadHeight").text = str(TARGET_MAX_LOAD_HEIGHT)
    ET.SubElement(dimensions, "MaxLoadWeight").text = str(TARGET_MAX_LOAD_WEIGHT)

    # Message > PalletInit : Pallets > Pallet : Overhang
    overhang = ET.SubElement(pallet, "Overhang")
    ET.SubElement(overhang, "Length").text = "0"
    ET.SubElement(overhang, "Width").text = "0"

    # Message > PalletInit : Pallets > Pallet : Security Margins
    securityMargins = ET.SubElement(pallet, "SecurityMargins")
    ET.SubElement(securityMargins, "Length").text = "0"
    ET.SubElement(securityMargins, "Width").text = "0"

    # Message > Order
    order = ET.SubElement(root, "Order")
    ET.SubElement(order, "ID").text = ORDERID
    ET.SubElement(order, "Description").text = "description"

    # Message > Order > Restriction
    restriction = ET.SubElement(order, "Restrictions")
    ET.SubElement(restriction, "FamilyGrouping").text = "False"
    ET.SubElement(restriction, "Ranking").text = "False"

    # Message > Order > OrderLines
    orderlines = ET.SubElement(order, "OrderLines")
    for i, ol in enumerate(BENDATA_ORDERLINES):
        # Message > Order > OrderLines > OrderLine
        orderline = ET.SubElement(orderlines, "OrderLine")
        ET.SubElement(orderline, "OrderLineNo").text = str(i + 1)
        # Message > Order > OrderLines > OrderLine : Article
        article = ET.SubElement(orderline, "Article")
        ET.SubElement(article, "ID").text = str(ol["properties"]["id"])
        ET.SubElement(article, "Description").text = str(ol["properties"]["article"])
        ET.SubElement(article, "Type").text = str(1)
        ET.SubElement(article, "Length").text = str(int(ol["properties"]["length/mm"]))
        ET.SubElement(article, "Width").text = str(int(ol["properties"]["width/mm"]))
        ET.SubElement(article, "Height").text = str(int(ol["properties"]["height/mm"]))
        ET.SubElement(article, "Weight").text = str(round(ol["properties"]["weight/kg"]))
        ET.SubElement(article, "Family").text = str(i + 1)  # need ints as base
        barcodes = ET.SubElement(orderline, "Barcodes")
        for bcode in ol["barcodes"]:
            ET.SubElement(barcodes, "Barcode").text = bcode

    # save the created tree
    tree = ET.ElementTree(root)
    __indent(root)
    tree.write(f"order_{order_id}.xml", xml_declaration=True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This file converts the orders of the bed-bpp_env repo to a format that can be used by the solver `josch/sisyphus`, which was developed for VMAC 2012."
    )
    parser.add_argument("--order_id", type=str, help="The id of the order that is converted.", required=True)
    parser.add_argument(
        "--src_order", type=str, help="The file that contains the order that is converted.", required=True
    )
    args = parser.parse_args()

    convertOrder(src_order=args.src_order, order_id=args.order_id)
