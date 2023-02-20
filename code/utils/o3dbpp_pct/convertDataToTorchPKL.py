'''
Converts a json file that contains orders to a .pkl file with torch. This .pkl file can be used for the evaluation of a solver of `alexfrom0815/Online-3D-BPP-PCT`. Note that these converted files start with an empty order and end with an empty order, since otherwise an IndexError occurs when evaluating the amount of orders that are originally in that file.  

After the conversion, a summary of the contained items and targets is printed to a logfile.  
'''
import utils
import argparse
import json
import pathlib
import environment
import logging
import torch
from tqdm import tqdm


logger = logging.getLogger(__name__)
loggingfile = utils.OUTPUTDIRECTORY.joinpath("torchconverter_logs.log")
logger.addHandler(logging.FileHandler(loggingfile))



def convertJSONDataToEvaluationPKL(src_order:pathlib.Path) -> None:
    '''
    Converts a json file that contains orders to a .pkl file with torch. This pkl file can be used for the evaluation of a solver of `alexfrom0815/Online-3D-BPP-PCT`. Note that these converted files start with an empty order and end with an empty order, since otherwise an IndexError occurs when evaluating the amount of orders that are originally in that file.  

    Parameters.
    -----------
    src_order: pathlib.Path  
        The path to the file that is converted.  
    '''
    inputFilename = src_order
    outputFilename = f"{inputFilename.stem}.pkl"

    with open(inputFilename) as file:
        benchmarkData = json.load(file, parse_int=False)


    outputList = [[]]

    listLengths = []
    listWidths = []
    listHeights = []
    targetSizes = {}

    # iterate over the input data
    for orderId, values in tqdm(benchmarkData.items()):
        orderList = []
        
        for value in values["item_sequence"].values():
            l = int(value.get("length/mm")/10)
            if not(l in listLengths): listLengths.append(l)
            w = int(value.get("width/mm")/10)
            if not(w in listWidths): listWidths.append(w)
            h = int(value.get("height/mm")/10)
            if not(h in listHeights): listHeights.append(h)
            density = round((l*w*h)/value.get("weight/kg"), 6)
            orderList.append(tuple([l,w,h,density]))

        target = values["properties"]["target"]
        if target=="rollcontainer" and not(f"{target}/cmxcmxcm" in targetSizes.keys()): targetSizes[f"{target}/cmxcmxcm"] =  [int(size/10) for size in environment.SIZE_ROLLCONTAINER] + [int(environment.MAXHEIGHT_TARGET/10)]
        elif target=="euro-pallet" and not(f"{target}/cmxcmxcm" in targetSizes.keys()): targetSizes[f"{target}/cmxcmxcm"] = [int(size/10) for size in environment.SIZE_EURO_PALLET] + [int(environment.MAXHEIGHT_TARGET/10)]

        # append the converted order
        outputList.append(orderList)
    # finally, append an empty list
    outputList.append([])


    # write the converted data to a file
    outputFile = utils.OUTPUTDIRECTORY.joinpath(outputFilename)
    with open(outputFile, "wb") as file:
        torch.save(outputList, file)


    # sort the values
    listLengths.sort()
    listWidths.sort()
    listHeights.sort()

    # log a summary of the elements in the converted order
    itemSizeStr = "conversion summary (might be used for `Online-3D-BPP-PCT>givenData.py` for training):\n"
    itemSizeStr += "summary of the contained items.\n"
    itemSizeStr += "-------------------------------\n"
    itemSizeStr += f"  x/cm: {listLengths}\n"
    itemSizeStr += f"  y/cm: {listWidths}\n"
    itemSizeStr += f"  z/cm: {listHeights}\n"
    itemSizeStr += "value range of the contained items.\n"
    itemSizeStr += "-----------------------------------\n"
    itemSizeStr += f"  x/cm: {[min(listLengths), max(listLengths)]}\n"
    itemSizeStr += f"  y/cm: {[min(listWidths), max(listWidths)]}\n"
    itemSizeStr += f"  z/cm: {[min(listHeights), max(listHeights)]}\n"
    itemSizeStr += "target sizes.\n"
    itemSizeStr += "-------------\n"
    for key, value in targetSizes.items():
        itemSizeStr += f"  {key}: {value}\n"

    print(itemSizeStr)
    logger.info(itemSizeStr)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


if __name__=='__main__':
    '''
    Main of the converter.
    '''
    parser = argparse.ArgumentParser(description='Possible arguments for the results converter BED-BPP format => Online-3D-BPP-PCT. The converted file can be used for `evaluation.py` of the solver.')
    parser.add_argument('--src_order', type=str, default=utils.getPathToExampleData().joinpath("benchmark_data/bed-bpp_v1.json"), help="The order data that is converted to a torch pkl file.")
    args = parser.parse_args()
    
    if not(isinstance(args.src_order, pathlib.Path)): args.src_order = pathlib.Path.cwd().joinpath(args.src_order)
    convertJSONDataToEvaluationPKL(src_order=args.src_order)



