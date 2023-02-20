'''
The module `PalletizingEnvironment` contains a class that is based on OpenAI's `gym` API that can easily be used for palletizing simulations.   

Depending on the task, e.g., `"O3DBP-k-s"`, the dictionary that contains additional information after a `reset` or `step` call, holds a different amount of next items. The `s` items an agent can choose to place next are stored in this dictionary with the key `"next_items_selection"`. In order to know which `k-s` items come after the selection, get the list that is stored with the key `"next_items_preview"` in the info dictionary.  
'''
import configparser
from typing import Tuple
import pathlib
import cv2
import environment
import evaluation
import json
import gym
from gym.spaces import Discrete, Dict, Box
import logging
import numpy as np
import PIL
from PIL import Image, ImageDraw, ImageFont
import platform
from visualization import PalletizingEnvironmentVisualization as EnvironmentVisualization

logger = logging.getLogger(__name__)

SIZE_ROLLCONTAINER = environment.SIZE_ROLLCONTAINER
'''The base area of the target "rollcontainer" in millimeters.'''
SIZE_EURO_PALLET = environment.SIZE_EURO_PALLET
'''The base area of the target "euro-pallet" in millimeters.'''

MAXHEIGHT_OBSERVATION_SPACE = environment.MAXHEIGHT_OBSERVATION_SPACE
'''The maximum height of the observation space in millimeters.'''

import utils
RENDER = utils.PARSEDARGUMENTS.get("visualize", False)

conf = configparser.ConfigParser()
conf.read(utils.configuration.USEDCONFIGURATIONFILE)


class PalletizingEnvironment(gym.Env):
    '''
    The PalletizingEnvironment is a class that can be used for palletizing simulation. Since it is based on OpenAI `gym`, the known API can be used. The methods can be interpreted as  
    (a) `step`: palletize an item in which the given action defines the x- and y-coordinates of the item and its orientation. The z-coordinate is calculated within this method.    
    (b) `reset`: start the palletization of items, i.e., the first item of an order is considered and the palletizing target is empty.  
    (c) `render`: visualize the current status of the palletization.    
    (d) `close`: stop the palletization.    

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    Note

    We must save the heights in mm steps and provide the allowed areas in mm steps, since otherwise information gets lost and due to rounding errors we do not palletize them in the "best" positions.  
    '''
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self) -> None:
        self.__Size = SIZE_EURO_PALLET
        '''The palletizing target's size of the base area in x- and y-direction given in millimeters.'''
        self.__N_ORIENTATION = 2
        '''The amount of different orientations that are allowed during palletization.'''

        self.__SizeMultiplicator = 1
        '''TBD needed for rescalewrapper and isItemSelectable'''

        self.action_space = Dict({"x": Discrete(self.__Size[0]), "y": Discrete(self.__Size[1]), "orientation": Discrete(self.__N_ORIENTATION)})
        '''The action space consists of the simple action spaces for x-, y-coordinate and the orientation of the item.'''
        
        self.observation_space = Box(low=0, high=MAXHEIGHT_OBSERVATION_SPACE, shape=(self.__Size[1], self.__Size[0]), dtype=int)
        '''The observation space describes the heights in each coordinate on the palletizing target.'''

        self.__TargetSpace = environment.Space3D(self.__Size)
        '''Represents the 3D space where the palletization takes place.'''
        
        self.__Actions = []
        '''A list that stores all actions done in the order of their palletizing point in time.'''

        self.__PalletizedVolume = 0.0
        '''A float that stores the palletized volume of all items in cm^3.'''

        self.__Orders = {}
        '''The orders that are given whenever the method `reset` is called with a non-empty parameter `data_for_episodes`. The format is identical to the format of the benchmark data.'''
        self.__CurrentOrder = {}
        '''This dictionary has the keys `"key"`, `"order"`, and `"seq"`, whose values store the key of the order as given in the order data, the current order itself, and the number in the sequence of all orders, respectively.'''
        self.__OrderSequence = [] # list of the keys of the given order data
        '''This list contains all keys in the order data in the same order as it is given.'''
        self.__ItemSequenceCounter = None
        '''This integer stores the position within an item sequence of the current order.'''

        self.__Visualization = None
        '''This object creates a visualization of the current palletizing status.'''

        self.__PackingPlans = {}
        '''The created packing plans of the solver/agent.'''

        self.__NItemPreview = int(conf.get("environment", "preview"))
        '''The amount of preview items.'''
        self.__NItemSelection = int(conf.get("environment", "selection"))
        '''The amount of items to select from, i.e., to select for the next step.'''

        self.__ItemsSelection = []
        '''The items to select from for the next palletizing step.'''
        self.__ItemsPreview = []
        '''The preview items.'''

        self.__KPIs = evaluation.KPIs()
        '''Holds the values of the KPIs for each order.'''


    def step(self, action:dict) -> Tuple[np.ndarray, float, bool, dict]:
        '''
        In the step function we have to palletize the given item at the given position. Translated to this implementation that means that we have to  
        (a) calculate the z-coordinate of the placement for the given action (x-,y-coordinate and orientation of item),     
        (b) append the item to the palletized items,    
        (c) update the height map of the palletizing target,    
        (d) obtain the allowed positions for the upcoming item,     
        (e) obtain the reward of the step, and  
        (f) obtain the additional information.  

        Parameters.
        -----------
            action: dict    
                The action contains the `"x"` and `"y"` coordinate of the placement, the item and its `"orientation"`.  

        Returns.
        --------
            stepReturns: tuple  
                The step method returns the new observation (`object`), the reward (`float`), whether the episode has ended (`bool`) and additional information (`dict`).   

        Examples.
        ---------
        >>> action = {
                "x": 100, # int
                "y": 100, # int
                "orientation": 0, # int
                "item": {'article': 'cake-00104295', 'id': 'c00104295', 'product_group': 'confectionery', 'length/mm': 590, 'width/mm': 200, 'height/mm': 210, 'weight/kg': 7.67, 'sequence': 1}
            }
        '''
        info = {} 

        # get the variables that are needed here
        sVars = self.__getStepVariables(action)
        itemForAction = action["item"]
        if not(self.__isItemSelectable(itemForAction)): raise ValueError(f"item {itemForAction} must not be selected.")

        # define the item
        item = environment.Item3D(itemForAction)
        item.setOrientation(sVars["orientation"])
    
        # create a np.ndarray that has the same shape as the target, its elements are 1 if the item is located in this region and 0 otherwise
        itemOnTarget = np.zeros((self.__Size[1], self.__Size[0]), dtype=int)
        itemDeltaY, itemDeltaX = item.getRepresentation().shape
        startX, startY = sVars["xCoord"], sVars["yCoord"]         
        try:
            itemOnTarget[startY:startY+itemDeltaY, startX:startX+itemDeltaX] = np.ones(item.getRepresentation().shape, dtype=int)
        except:
            # have to crop item like in `environment.Space3D.addItem`
            logger.warning(f"cropped item")
            croppedShape = (min(itemOnTarget.shape[0], startY+itemDeltaY)-startY, min(itemOnTarget.shape[1], startX+itemDeltaX)-startX)
            itemOnTarget[startY:startY+croppedShape[0], startX:startX+croppedShape[1]] = np.ones(croppedShape, dtype=int)

        # obtaiin the FLB height for the item in the selected (x, y)-coordinate
        maxHeightInTargetArea = int(np.amax(np.multiply(self.__TargetSpace.getHeights(), itemOnTarget)))


        # define the action in the needed format
        actionExt = {
            "item": itemForAction,
            "flb_coordinates": [sVars["xCoord"], sVars["yCoord"], maxHeightInTargetArea],
            "orientation": sVars["orientation"]
        }
        self.__Actions.append(actionExt)
        info.update({"action_for_vis": actionExt})
        logger.info(f"step() -> extended action: {actionExt}")

        # add the item to the palletizing target
        self.__TargetSpace.addItem(item, actionExt["orientation"], actionExt["flb_coordinates"])
        info.update({"support_area/%": item.getPercentageDirectSupportSurface()})


        # prepare for next call of step
        additionalInfo = self.__prepareForNextStep(itemForAction)
        done = additionalInfo.pop("done")
        info.update(additionalInfo)


        # update the attributes
        self.__updatePalletVisualization(actionExt)
        self.__PalletizedVolume += (sVars["deltaX"]*sVars["deltaY"]*sVars["itemHeight"])/1000.0
        self.__KPIs.update()
        

        reward = self.__getReward(done)
        info = self.__getInfo("step", info)

        stepReturns = self.__TargetSpace.getHeights(), reward, done, info
        return stepReturns


    def reset(self, data_for_episodes:dict = {}) -> Tuple[np.ndarray, dict]:
        '''
        This method is responsible for  
        (a) the change of the orders, e.g., from "00100001" -> "00100002",  
        (b) the reset of the stored attributes and heights of the virtual palletizing target,   
        (c) obtaining the inital observation and information about the environment,     
        (d) resetting the target's size of the base area, depending on the goal that is defined in the given data for the episodes, and     
        (e) loading the order data that shoud be considered.    

        Parameters.
        -----------
        data_for_epsidoes: dict (default = {})      
            The data for the episodes in the format of the benchmark data.  

        Returns.
        --------
        observation: np.array   
            The stored heights of the environment.  
        info: dict  
            A dictionary that contains additional information that might be useful for the machine learning agent.  
        '''
        self.__savePackingPlan()
        # # # # # Change the Order that is considered # # # # #
        done = False
        # change the current order
        if self.__CurrentOrder=={} or not(data_for_episodes=={}):
            self.__Orders = data_for_episodes
            self.__OrderSequence = list(self.__Orders.keys())
            self.__CurrentOrder["seq"] = 0
            orderKey = self.__OrderSequence[self.__CurrentOrder["seq"]]
            self.__CurrentOrder["key"] = orderKey
            self.__CurrentOrder["order"] = self.__Orders[orderKey]

        elif self.__CurrentOrder["seq"]+1 >= len(self.__OrderSequence):
            # reached the last order in the data
            done = True
            self.__CurrentOrder["seq"] += 1
            
        else:
            self.__CurrentOrder["seq"] += 1
            orderKey = self.__OrderSequence[self.__CurrentOrder["seq"]]
            self.__CurrentOrder["key"] = orderKey
            self.__CurrentOrder["order"] = self.__Orders[orderKey]

        if not(done):
            logger.info(f"CURRENT ORDER:{self.__CurrentOrder}\n\n\n")


        # # # # # Reset the Attributes # # # # #
        self.__ItemSequenceCounter = 1
        # change the size related to the palletizing target and the action space
        palletizingTarget = self.__CurrentOrder["order"]["properties"]["target"]
        if palletizingTarget == "rollcontainer":
            self.__Size = SIZE_ROLLCONTAINER
        elif palletizingTarget == "euro-pallet":
            self.__Size = SIZE_EURO_PALLET
        else:
            # size is given as `"x,y,z"`
            sizes = palletizingTarget.split(",")
            self.__Size = tuple([int(sizes[0]), int(sizes[1])])
        
        self.action_space = Dict({"x": Discrete(self.__Size[0]), "y": Discrete(self.__Size[1]), "orientation": Discrete(self.__N_ORIENTATION)})

        del self.__Visualization
        self.__Visualization = EnvironmentVisualization(visID=self.__CurrentOrder["key"], target=palletizingTarget)

        self.__TargetSpace.reset(self.__Size)
        self.__Actions = []
        self.__PalletizedVolume = 0.0
        self.__KPIs.reset(self.__TargetSpace, self.__CurrentOrder)

        self.__ItemsSelection = []
        self.__ItemsPreview = []
        if not(done):
            # only update items if we do not 
            self.__updateItemsSelection()
            self.__updateItemsPreview()

        # # # # # Obtain the Observation and Info # # # # #
        observation = self.__TargetSpace.getHeights()
        info = self.__getInfo("reset")


        return observation, info


    def render(self, mode="human") -> None:
        '''
        Renders the environment.  
        
        Note.
        -----
        If you want to save the displayed render image, you have to uncomment two lines below in this method.
        '''
        if not(RENDER):
            return None

        DISPLAYTIME = 100 # ms

        renderImage = Image.new("RGB", (1800, 900), color=(255, 255, 255))
        testStatus = Image.open(self.__Visualization.getFilenameOfImage()) 
        testStatus = testStatus.resize((800,800))
        renderImage.paste(testStatus, (0,0))

        draw = ImageDraw.Draw(renderImage)
        if self.__Actions == []:
            pass
        else:
            # find path for font
            usedPlatforn = platform.platform()
            if "macOS" in usedPlatforn:
                pathToFont = "~/Library/Fonts/Arial Unicode.ttf"
            elif "Linux" in usedPlatforn:
                pathToFont = "/usr/share/fonts/opentype/cabin/Cabin-Regular.otf"
            else:
                # windows is currently not implemented
                pass

            fontHeader = ImageFont.truetype(pathToFont, size=30)
            fontTxt = ImageFont.truetype(pathToFont, size=20)

            action = self.__Actions[-1]
            item = action["item"]
            txtItem = ""
            for key, value in item.items():
                txtItem += f"{key}: {value}\n"

            draw.text((700, 5), "Item", font=fontHeader, fill ="black", align ="left")
            draw.text((700, 40), txtItem, font=fontTxt, fill ="black", align ="left") 

            coordinateFromAction = action["flb_coordinates"]
            draw.text((1000, 5), "FLB Coordinates", font=fontHeader, fill ="black", align ="left")
            draw.text((1000, 40), str(coordinateFromAction), font=fontTxt, fill ="black", align ="left") 

            orientation = action["orientation"]
            draw.text((1000, 85), "Orientation", font=fontHeader, fill ="black", align ="left")
            draw.text((1000, 120), str(orientation), font=fontTxt, fill ="black", align ="left") 


            draw.text((1300, 5), "KPIs", font=fontHeader, fill ="black", align ="left")
            kpis = self.__KPIs.getPrettyStr()
            draw.text((1300, 40), kpis, font=fontTxt, fill ="black", align ="left") 


            palletHeights = self.__TargetSpace.getHeights()
            draw.text((700, 300), f"State of Env (h {MAXHEIGHT_OBSERVATION_SPACE}mm => white)", font=fontHeader, fill ="black", align ="left")
            draw.text((700, 335), f"Size = {palletHeights.shape}", font=fontTxt, fill ="black", align ="left")
            
            testState = Image.fromarray((palletHeights*255/2500).astype(float))#np.uint8))
            hflippedtestState = testState.transpose(PIL.Image.FLIP_TOP_BOTTOM)
            hflippedtestState = hflippedtestState.resize((hflippedtestState.size[0]//2,hflippedtestState.size[1]//2))
            renderImage.paste(hflippedtestState, (700, 365))

        # # uncomment the lines below if you want to save the render image
        # fname = f"vis_{self.__CurrentOrder['key']}_{self.__ItemSequenceCounter}.png" # "render_image.png"
        # targetpathForRenderImage = pathlib.Path.joinpath(utils.OUTPUTDIRECTORY, fname)
        # renderImage.save(targetpathForRenderImage)

        windowname = "BED-BPP Environment | Render Image"
        cv2.namedWindow(windowname)#, cv2.WINDOW_NORMAL)
        cv2.moveWindow(windowname, 0, 0)
        # cv2.setWindowProperty(windowname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        img1 = cv2.cvtColor(np.array(renderImage), cv2.COLOR_RGB2BGR)
        cv2.imshow(windowname, img1)
        cv2.waitKey(DISPLAYTIME)


    def close(self) -> None:
        self.__savePackingPlan(True)


    # utils

    def __isItemSelectable(self, itemdict:dict) -> bool:
        '''
        This method checks whether the item that is given in an action is selectable in the current situation.  

        Parameters.
        -----------
        item: environment.Item3D  
            tbd.  
        
        Returns.
        --------
        selectable: bool  
            Indicates whether the item is selectable.  
        '''
        selectable = False
        
        tempdict = itemdict
        if not(self.__SizeMultiplicator==1):
            # adapt the item size whenever the RescaleWrapper is used
            tempdict["length/mm"] *= self.__SizeMultiplicator[0]
            tempdict["width/mm"] *= self.__SizeMultiplicator[1]

        if tempdict in self.__ItemsSelection:
            selectable = True

        return selectable


    def __savePackingPlan(self, tofile:bool=False) -> None:
        if self.__CurrentOrder=={}:
            # do nothing
            pass
        else:
            orderKey = self.__CurrentOrder["key"]
            if not(orderKey in self.__PackingPlans.keys()):
                self.__PackingPlans[orderKey] = self.__Actions

                packingPlan = {
                    orderKey: self.__Actions
                }
                logger.info(f"PackingPlan = {packingPlan}")

        if True:#tofile:
            packingPlansFile = "packing_plans.json"
            outputFile = pathlib.Path.joinpath(utils.OUTPUTDIRECTORY, packingPlansFile)
            with open(outputFile, "w") as PPFile:
                json.dump(self.__PackingPlans, PPFile)


    def __getReward(self, done:bool) -> float:
        '''
        You can define your reward here.
        '''
        if done:
            reward = 1.0
        else:
            reward = 0.0
        return reward


    def __getInfo(self, calledby:str="step", additionalinfo:dict={}) -> dict:
        '''Get the info dictionary after reset or step.'''
        info = additionalinfo

        if calledby == "step":
            info.update({
                "all_orders_considered": None,
                "item_volume_on_target/cm^3": self.__PalletizedVolume,
                "n_items_in_order": len(self.__CurrentOrder["order"]["item_sequence"])
            })

        elif calledby == "reset":
            # obtain whether all orders are considered
            done = self.__CurrentOrder["seq"] >= len(self.__OrderSequence) # do not need +1 because the counter is already increased

            if not(done):
                # obtain np.array with allowed area
                nextItems = self.__obtainNextItems()
                item = nextItems["selection"][0]
                allowedArea = self.__obtainAllowedAreas(item)

                cornerPoints = self.__determineCornerPoints(nextItems["selection"])


                info.update({ 
                    "all_orders_considered": done,
                    "allowed_area": allowedArea,
                    "order_id": self.__CurrentOrder["key"],
                    "palletizing_target": self.__CurrentOrder["order"]["properties"]["target"],
                    "next_items_selection": nextItems["selection"],
                    "next_items_preview": nextItems["preview"],
                    "n_items_in_order": len(self.__CurrentOrder["order"]["item_sequence"]),
                    "corner_points": cornerPoints
                })

            else:
                # all orders considered
                info.update({ 
                    "all_orders_considered": done,
                    "allowed_area": {},
                    "order_id": None,
                    "palletizing_target": None,
                    "next_items_selection": [],
                    "next_items_preview": [],
                    "n_items_in_order": None,
                    "corner_points": {}
                })

        return info


    def __getStepVariables(self, action:dict) -> dict:
        '''This method creates the variables that are needed in the `step` method, depending on the given action. '''
        orientation = action["orientation"]
        xCoord, yCoord = int(action["x"]), int(action["y"])

        item = action["item"]
        itemLength, itemWidth, itemHeight = int(item["length/mm"]), int(item["width/mm"]), int(item["height/mm"])

        if orientation == 0:
            deltaX, deltaY = itemLength, itemWidth
        elif orientation == 1:
            deltaX, deltaY = itemWidth, itemLength

        stepVar = {
                    "xCoord": xCoord,
                    "yCoord": yCoord,
                    "deltaX": deltaX,
                    "deltaY": deltaY, 
                    "itemHeight": itemHeight,
                    "orientation": orientation,
        }
        
        return stepVar


    def __obtainAllowedAreas(self, item:dict) -> dict:
        '''
        This method returns a dictionary that contains np.arrays, which define in which coordinates the given item can be placed.  
        Returns.
        --------
        allowedArea: dict
            A dictionary whose keys define the orientation and the values define the possible coordinates of an item placement.

        Example.
        --------
        >>> allowedArea = {
                0: np.array,
                1: np.array,
                <orientation>: np.array # element == 1: allowed; element == 0: not allowed
            }
        '''
        allowedArea = {}

        # create the arrays such that the item is completely inside the palletizing target
        itemLength, itemWidth = int(item["length/mm"]), int(item["width/mm"])
        for orientation in range(self.__N_ORIENTATION):
            if orientation == 0:
                deltaX, deltaY = itemLength, itemWidth
            elif orientation == 1:
                deltaX, deltaY = itemWidth, itemLength

            if (self.__Size[1] >= deltaY) and (self.__Size[0] >= deltaX):
                # check whether the items can be placed in the target
                allowedCoordinates = np.zeros((self.__Size[1], self.__Size[0]), dtype=int)
                allowedCoordinates[0:self.__Size[1]-deltaY, 0:self.__Size[0]-deltaX] = np.ones((self.__Size[1]-deltaY, self.__Size[0]-deltaX))
                allowedArea[orientation] = allowedCoordinates
    
        return allowedArea


    def __prepareForNextStep(self, placeditem:dict) -> dict:
        '''
        This method prepares the environment for the next call of the `step` method. Hence, the __ItemSequenceCounter is increased and the next palletizing items and their allowed positions on the target are calculated, unless the current episode has not finished (after the currently called `step`).

        Returns.
        --------
        info: dict  
            Information that is returned by the `step` method.  
        '''
        info = {}

        self.__ItemSequenceCounter += 1
        if self.__ItemSequenceCounter > len(self.__CurrentOrder["order"]["item_sequence"]):
            done = True # episode finished
            info.update({"allowed_area": {0: np.zeros((self.__Size), dtype=int), 1: np.zeros((self.__Size), dtype=int)}, 
                        "next_items_selection": [],
                        "next_items_preview": []                        
                        })
        else:
            done = False
            self.__updateItemsSelection(placeditem)
            self.__updateItemsPreview()
            nextItems = self.__obtainNextItems()
            item = nextItems["selection"][0]
            allowedArea = self.__obtainAllowedAreas(item)
            

            # get the corner points for the items that can be selected
            cornerPoints = self.__determineCornerPoints(nextItems["selection"])

                
            info.update({"allowed_area": allowedArea, 
                         "next_items_selection": nextItems["selection"],
                         "next_items_preview": nextItems["preview"],
                         "corner_points": cornerPoints
                         })


        info.update({"done": done})

        return info


    def __obtainNextItems(self) -> dict:
        '''
        Returns a dictionary that contains the next items in the item sequence of order that is currently considered. Depending on the task, i.e., on the specified values for the preview `k` and the selection `s`, the lenght of the returned item list differs.  

        As example, if the task `"O3DBP-k-s"` is loaded, then the length of the list with the selection items is `s`, and the list of the preview items is `k-s`. In general, the preview list is not empty, if and only if `k > s`.  

        If less items are left in the item sequence as the values of `k` and `s` would request, instead of the item's properties an empty dictionary is appended.  
        
        Returns.
        --------
        nextItems: dict  
            Contains the next items in the item sequence.  

        Examples.
        ---------
        >>> self.__obtainNextItems() # with k=s=1
        {
            "selection": [{"article": "article_1", "id": "id_1", "product_group": "pg_1", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 1}],
            "preview": []
        }
        >>> self.__obtainNextItems() # with k=3; s=1
        {
            "selection": [{"article": "article_1", "id": "id_1", "product_group": "pg_1", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 1}],
            "preview": [{"article": "article_2", "id": "id_2", "product_group": "pg_2", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 2}, {"article": "article_3", "id": "id_3", "product_group": "pg_3", "length/mm": 400, "width/mm": 300, "height/mm": 200, "weight/kg": 2, "sequence": 3}]
        }
    
        '''
        nextItems = {
            "selection": self.__ItemsSelection,
            "preview": self.__ItemsPreview
        }
        return nextItems


    def __updateItemsSelection(self, itemdict:dict={}) -> None:
        '''
        This method updates the items that can be selected.  

        Parameters.
        -----------
        itemdict: dict  
            The properties of the item that was palletized in the last `env.step` call.  
        
        Important.
        ----------
        Call this method before `self.__updateItemsPreview`.  
        '''
        if (self.__ItemSequenceCounter==1) or (len(self.__ItemsPreview)==0):
            if not(self.__ItemSequenceCounter==1): 
                # not first call -> remove itemdict from selection
                self.__ItemsSelection.remove(itemdict)
            # first call in env.reset in an episode
            for s in range(self.__NItemSelection):
                itemKey = str(self.__ItemSequenceCounter+s)
                if itemKey in self.__CurrentOrder["order"]["item_sequence"].keys():
                    self.__ItemsSelection.append(self.__CurrentOrder["order"]["item_sequence"][str(self.__ItemSequenceCounter+s)])
                else:
                    self.__ItemsSelection.append({})
        else:
            # call in env.step
            self.__ItemsSelection.remove(itemdict)
            self.__ItemsSelection.append(self.__ItemsPreview.pop(0))


    def __updateItemsPreview(self) -> None:
        '''
        This method updates the items that are known in advance, but cannot be selected.  

        Important.
        ----------
        Call this method after `self.__updateItemsSelection`.  
        '''
        for k in range(self.__NItemSelection, self.__NItemPreview):
            itemCounter = self.__ItemSequenceCounter+k
            itemKey = str(itemCounter)
            if itemKey in self.__CurrentOrder["order"]["item_sequence"].keys():
                prevItem = self.__CurrentOrder["order"]["item_sequence"][itemKey]
                if not(prevItem in self.__ItemsPreview):
                    self.__ItemsPreview.append(prevItem)
            else:
                nPurePrevItems = self.__NItemPreview-self.__NItemSelection
                if not(len(self.__ItemsPreview) >= nPurePrevItems): 
                    self.__ItemsPreview.append({})


    def __updatePalletVisualization(self, action:dict) -> None:
        item = action["item"]
        flbcoordinates = action["flb_coordinates"]
        orientation = action["orientation"]
        if orientation == 0:
            lcProps = {
                "cont_id": item["id"],
                "length": item["length/mm"],
                "width": item["width/mm"],
                "height": item["height/mm"],
                "sku": item["article"]
            }
        elif orientation == 1:
            lcProps = {
                "cont_id": item["id"],
                "length":  item["width/mm"],
                "width": item["length/mm"],
                "height": item["height/mm"],
                "sku": item["article"]
            }

        lcTarget = {
            "area": "area",
            "x": flbcoordinates[0],
            "y": flbcoordinates[1],
            "z": flbcoordinates[2]
        }

        lc = environment.LC(lcProps)
        lc.setTargetposition(lcTarget)
        self.__Visualization.addLoadCarrier(lc)
        self.__Visualization.updateVisualization()


    def __determineCornerPoints(self, possibleitems:list) -> dict:
        '''
        Determines the corner points for all items that are given.  

        Parameters.
        -----------
        possibleitems: list  
            Contains the item dictionary of the items that could be selected for palletization.  

        Returns.
        --------
        cornerPoints: list  
            The corner points for an item that is specified by its dimension.  
        '''
        cornerPoints = {}
        for item in possibleitems:
            itemArticle = item.get("article", None)
            if not(itemArticle is None):
                cornerPoints[itemArticle] = {}
                for orientation in range(self.__N_ORIENTATION):
                    if orientation==0:
                        length, width, height = item.get("length/mm"), item.get("width/mm"), item.get("height/mm")
                    elif orientation==1:
                        width, length, height = item.get("length/mm"), item.get("width/mm"), item.get("height/mm")
                    
                    cornerPoints[itemArticle][orientation] = self.__TargetSpace.getCornerPointsIn3D((length, width, height))

        return cornerPoints


    def setSizeMultiplicator(self, size_multiplicator:tuple) -> None:
        '''
        This method is called whenever the RescaleWrapper is used.  
        '''
        self.__SizeMultiplicator = size_multiplicator
