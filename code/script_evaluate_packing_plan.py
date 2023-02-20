'''
This script evaluates a packing plan, i.e., a Blender stability check is performed and the KPIs of the packing plan are calculated.  
'''
import utils
import evaluation
from evaluation import EVALOUTPUTDIR
import json
import logging
import subprocess
import gc
import time
import pathlib
import platform

logger = logging.getLogger(__name__)

ppEvaluator = evaluation.PackingPlanEvaluator()
'''An instance of PackingPlanEvaluator that evaluates the given packing plan.'''


def evaluatePackingPlan(id:str, order:dict, packingplan:list) -> None:
    '''
    This methods evaluates the given packing plan with a PackingPlanEvaluator instance.  

    Parameters.
    -----------
    id: str  
        The id of the order.  
    order: dict  
        The order that correpsonds to the packing plan that is evaluated.  
    packingplan: list  
        The packing plan that is evaluated.  
    '''
    ppEvaluator.evaluate(id, order, packingplan)


def runBlenderStabilityCheck(background:bool, orderid:str, renderscene:bool, actionplan:list, orderofpackingplan:dict, ordercolors:dict) -> None:
    '''
    This method calls blender to create a scene and start a rigid body simulation. Finally, the movement of all items during the simulation time is written to a file. For details see the file that is given by `blenderSceneGen`.  

    Parameters.
    -----------
    packingplan: str  
        The path to the packing plan as string.  
    order: str  
        The path to the order as string.  
    orderid: str
        The ID of the order.  
    actionplan: list  
        The list of actions for the given order.  
    orderofpackingplan: dict  
        The order that was the basis for the given packing plan.
    '''
    templFile = str(evaluation.blender.TEMPLATEFILE)
    blenderSceneGen = str(evaluation.blender.TEMPLATEFILE.parent.resolve().joinpath("scene_creation.py"))
    
    # cmd = ["blender"] # works only when "blender" is in PATH
    usedPlatform = platform.platform()
    if "macOS" in usedPlatform:
        cmd = ["/Applications/Blender.app/Contents/MacOS/Blender"]
    elif "Linux" in usedPlatform:
        cmd = ["/snap/blender/current/blender"]
    else:
        raise ValueError(f"platform {usedPlatform} is currently not implemented")

    if background: cmd += ["-b"]
    cmd += [templFile, "--python", blenderSceneGen, "--", "order_number", orderid, "output_dir", EVALOUTPUTDIR, "render", str(renderscene), "order_packing_plan", str(actionplan), "order", str(orderofpackingplan), "order_colors", str(ordercolors)]

    subprocess.run(cmd, shell=False)
    # run garbage collector -> it seems that the run of subprocess leads to a memory leak
    if not(int(orderid) % 10): gc.collect() # run every 10 orders


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

if __name__ == '__main__':
    # configure the parser of the given arguments
    parser = utils.arguments_parser.addGroupToParser("EvalPackingPlan", "the arguments of the packing plan evaluation")
    parser.add_argument("--data", type=str, default=utils.getPathToExampleData().joinpath("5_bed-bpp.json"), help="Defines which data is used.")
    parser.add_argument("--packing_plan", type=str, default=utils.getPathToExampleData().joinpath("packing_plan_5-bed-bpp.json"), help="Defines the packing plan that is evaluated.")
    parser.add_argument("-b", "--background", action="store_false", default=True, help="Indicates whether the Blender file should be opened.")
    parser.add_argument("-r", "--render", action="store_true", default=False, help="Indicates whether the created scenes are written to disk.")
    utils.arguments_parser.parse()
    args = utils.PARSEDARGUMENTS
    logger.info(f"got arguments: {args}")

    pathPackingPlan = pathlib.Path(args.get("packing_plan"))
    pathBenData = pathlib.Path(args.get("data"))
    notOpenBlender = args.get("background")

    with open(pathPackingPlan) as file:
        PACKINGPLANS = json.load(file, parse_int=False)

    with open(pathBenData) as file:
        BENDATA = json.load(file, parse_int=False)

    totalAmountOfItemsInBendata = 0
    for orderData in BENDATA.values():
        totalAmountOfItemsInBendata += len(orderData["item_sequence"])
    logger.info(f"have {totalAmountOfItemsInBendata} items in {pathBenData}")

    file_color_db = pathlib.Path(__file__).resolve().joinpath(f"../visualization/colors/colordb_{pathBenData.name}").resolve()
    with open(file_color_db) as file:
        COLOR_DB = json.load(file, parse_int=False)

    
    # Start Evaluation
    for orderID, actionPlan in PACKINGPLANS.items():
        bendataOrder = BENDATA.get(orderID)
        startTime = time.time()
        runBlenderStabilityCheck(background=notOpenBlender, 
                        orderid=orderID, 
                        renderscene=args.get('render'), 
                        actionplan=actionPlan, 
                        orderofpackingplan=bendataOrder, 
                        ordercolors=COLOR_DB[orderID])
        logger.info(f"blender stability check took {round(time.time() - startTime, 3)} seconds")
        evaluatePackingPlan(orderID, bendataOrder, actionPlan)
        logger.info(f"complete evaluation of order/packing plan took {round(time.time() - startTime, 3)} seconds")

        # free memory
        del BENDATA[orderID]
        if not(int(orderID)%500):
            gc.collect()


    ppEvaluator.writeToFile(totalAmountOfItemsInBendata)
