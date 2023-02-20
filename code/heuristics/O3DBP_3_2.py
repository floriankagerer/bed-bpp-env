'''
This heuristic demonstrates the task O3DBP-3-2, i.e., it can choose one of the two next items to palletize and knows the dimensions of another item in advance. In every call of `getAction`, the heuristic selects the action with the highest score.  
'''
import copy
import environment.SimPalEnv
import logging
import numpy as np
from typing import Tuple
import multiprocessing
import time
import gc

logger = logging.getLogger(__name__)

LIMIT_COMBINATIONS_AMOUNT = True
N_LIMIT_COMBINATIONS = 25
MULTI_PROCESSING_CHUNKSIZE = 1000


class O3DBP_3_2():
    '''
    This heuristic demonstrates the task O3DBP-3-2, i.e., it can choose one of the two next items to palletize and knows the dimensions of another item in advance. In every call of `getAction`, the heuristic selects the action with the highest score.  

    Parameters.
    -----------
    preview: int (default = 3)  
        The amount of known items.  
    selection: int (default = 2)  
        The amount of items that can be seleceted for the next palletizing step.  

    Attributes.
    -----------
    __Info: dict    
        The additional info that is provided by the palletizing environment.  
    FUNC_VECTORSCOREEVAL: np.vectorize function  
        Vectorized function to make the dot product of weights and components of score.  
    __NPreview: int  
        The amount of known items in advance.  
    __NSelection: int  
        The amount of items that are selectable for the next palletizing step.  
    __SCORE_WEIGHTS: list  
        The weights that are used to determine the score of an action.  
    __SimEnvironment: "environment.SimPalEnv"  
        A deepcopy of the palletizing environment for which an action is determined. This deepcopy is needed for estimating the scores of the possible actions.  
    '''
    def __init__(self, preview:int=3, selection:int=2) -> None:
        self.__SimEnvironment = None
        '''A deepcopy of the palletizing environment for which an action is determined. This deepcopy is needed for estimating the scores of the possible actions.'''

        self.__NPreview = preview
        '''The amount of known items in advance.'''
        self.__NSelection = selection
        '''The amount of items that are selectable for the next palletizing step.'''
        logger.info(f"heuristic set for selection={self.__NSelection} and preview={self.__NPreview}")
        
        self.__SCORE_WEIGHTS = [1.3, -2.0, -1.00001, -1.2]
        '''The weights that are used to determine the score of an action.'''
        logger.info(f"used the scores {self.__SCORE_WEIGHTS} for rating of corner points.")

        self.FUNC_VECTORSCOREEVAL = np.vectorize(self.multiplyWeightScore, excluded=[1], signature="(n)->()")
        '''Vectorized function to make the dot product of weights and components of score.'''


    def setSimEnv(self, environment:"environment.SimPalEnv") -> None:
        '''
        Sets an environment that is needed for simulations when having preview or selection.  

        Parameters.
        -----------
        environment: `environment.SimPalEnv`  
            Identical to the current state of `environment.PalletizingEnvironment`, but without any render methods. These were removed because these methods could not be pickled, which is needed when using `multiprocessing`.  
        '''
        self.__SimEnvironment = environment


    def getAction(self, observation:np.ndarray, info:dict) -> Tuple[dict, bool]:
        '''
        Return an action, depending on the given observation and information.   

        Parameters.
        -----------
        observation: np.ndarray     
            Contains the height values in each coordinate of the palletizing target in millimeters.  
        info: dict    
            Additional information about the palletizing environment. It must contain the keys `"allowed_area"`.  

        Returns.
        --------
        action: dict    
            Returns the selected item,`"x"`- and `"y"`-coordinates, and the item's `"orientation"` as ints.  
        foundAction: bool  
            Indicates whether the heuristic could find an action.  

        Example.
        --------
        >>> action = {
                "x": 100,
                "y": 100,
                "orientation": 0,
                "item": {'article': 'cake-00104295', 'id': 'c00104295', 'product_group': 'confectionery', 'length/mm': 590.0, 'width/mm': 200.0, 'height/mm': 210.0, 'weight/kg': 7.67, 'lc_type': 'tbd', 'sequence': 1}
            }
        '''
        possibleCP = self.__extractCornerPointsFromEnvironmentInfo(info.get("corner_points"))

        if len(possibleCP):
            firstCornerPointAction = self.__estimateCurrentCPScoreWithUpcomingItems(info, observation)
            successful = True
            # check whether corner point in origin should be taken
            if not(firstCornerPointAction["x"] == 0 and firstCornerPointAction["y"]):
                tempCornerPoint = firstCornerPointAction["x"], firstCornerPointAction["y"], None, firstCornerPointAction["orientation"]
                actionItem = firstCornerPointAction["item"]
                itemSize = actionItem["length/mm"], actionItem["width/mm"], actionItem["height/mm"]

                estimatedHeightInCP = self.__estimatePlacementZCoordinate(observation, tempCornerPoint, itemSize)

                heightOrigin = observation[0,0]
                if heightOrigin - estimatedHeightInCP  < -20:
                    logger.info(f"HEIGHT IN CORNER POINT IS TOO BIG -> SET CP to ORIGIN")
                    firstCornerPointAction = {
                        "x": 0,
                        "y": 0,
                        "orientation": 0,
                        "item": actionItem
                    }

        else:
            firstCornerPointAction = {
                "x": None,
                "y": None,
                "orientation": None,
                "item": None
            }   
            successful = False


        logger.info(f"heuristic selected action: {firstCornerPointAction}")
        if successful:
            _ = self.__SimEnvironment.step(firstCornerPointAction)
        
        return firstCornerPointAction, successful


    def __getScoreWeightsOfCornerPoint(self, observation:np.ndarray, cornerpoint:list, itemsize:list) -> float:
        '''
        Returns the components of the score of the action.  

        Parameters.
        -----------
        observation: np.ndarray  
            The observation of the environment.  
        cornerpoint: list  
            The corner point for which the score is calculated. The corner point looks like `[x, y, z, item_orientation]`.  
        itemsize: list  
            The size of the item.  

        Returns.
        --------
        score: float  
            The score of the given corner point.  

        Notes.
        ------
        The heuristic is desgined that it takes the action with the maximum score. Hence, this method must define that the best action has the highest score.  
        '''
        itemOrientation = cornerpoint[-1]

        estimatedSupportArea = self.__estimateSupportArea(observation, cornerpoint, itemsize)
        estimatedZCoordinate = self.__estimatePlacementZCoordinate(observation, cornerpoint, itemsize)
        
        distanceOrigin3D = self.__getDistanceToOrigin(cornerpoint, zcoordinate=estimatedZCoordinate, dimensions=3)
        # distanceOrigin2D = self.__getDistanceToOrigin(cornerpoint, dimensions=2)

        normedDistOrig3D = distanceOrigin3D/np.sqrt(np.square(observation.shape[0])+np.square(observation.shape[1])+np.square(2000))
        values = [estimatedSupportArea, estimatedZCoordinate/np.amax(observation, initial=estimatedZCoordinate), itemOrientation, normedDistOrig3D]
        return values


    def multiplyWeightScore(self, values:list, weights:list) -> float:
        '''
        Returns the dot product of values and weights.  

        Note.
        -----
        Must be public when multiprocessing is used.  
        '''
        if values.shape==(0,):
            # no values given
            values = [0]*len(weights)
        
        return np.dot(values, weights)


    def __estimatePlacementZCoordinate(self, observation:np.ndarray, cornerpoint: list, itemsize: list) -> int:
        '''
        Estimates the z-coordinate when an item is placed in the given cornerpoint.  

        Parameters.
        -----------
        observation: np.ndarray  
            The heights in each point of the target.  
        cornerpoint: list  
            The corner point for which the heigt should be esimated.  
        itemsize: list  
            The [length, width, height] of an item in millimeters.  

        Parameters.
        -----------
        estimatedHeight: int  
            The estimated height in the cornerpoint in milimeters.  
        '''
        cpXCoord, cpYCoord = cornerpoint[0], cornerpoint[1]
        itemOrientation = cornerpoint[-1]

        if itemOrientation==0:
            deltaX, deltaY = int(itemsize[0]), int(itemsize[1])
        elif itemOrientation==1:
            deltaX, deltaY = int(itemsize[1]), int(itemsize[0])

        estimatedHeight = np.amax(observation[cpYCoord:cpYCoord+deltaY, cpXCoord:cpXCoord+deltaX]) + itemsize[-1]
        return estimatedHeight


    def __estimateSupportArea(self, observation:np.ndarray, cornerpoint: list, itemsize: list) -> float:
        '''
        Estimates the direct support area of an item that is placed in the given cornerpoint. A height tolerance of 10 mm is used.  

        Parameters.
        -----------
        observation: np.ndarray  
            The heights on each point of the target.  
        cornerpoint: list (of length 4)  
            The coordinates of the cornerpoint and the item orientation for which the support area is estimated.  
        itemsize: list  
            The size of the item.  

        Returns.
        --------
        estimatedSuppArea: float  
            The estimated support area of the item.  
        '''
        cpXCoord, cpYCoord = cornerpoint[0], cornerpoint[1]
        itemOrientation = cornerpoint[-1]

        if itemOrientation==0:
            deltaX, deltaY = int(itemsize[0]), int(itemsize[1])
        elif itemOrientation==1:
            deltaX, deltaY = int(itemsize[1]), int(itemsize[0])

        placementArea = observation[cpYCoord:cpYCoord+deltaY, cpXCoord:cpXCoord+deltaX]
        maxHeightPlacementArea = np.amax(placementArea)

        # use tolerance of 10 mm
        tolerance = 10
        estimatedSuppArea = np.count_nonzero((placementArea > maxHeightPlacementArea-tolerance) & (placementArea < maxHeightPlacementArea+tolerance))/placementArea.size
        return estimatedSuppArea


    def __getDistanceToOrigin(self, cornerpoint:list, zcoordinate:float=None, dimensions:int=2) -> float:
        '''
        Returns the distance of the corner point to the origin in $\mathbb{R}^d$, where $d \in \{2, 3 \}$. For $d=2$ the distance to (0,0) is determined, for $d=3$ the distance to (0,0,0).  

        Parameters.
        -----------
        cornerpoint: list  
            The corner point for which the distance to origin is determined.  
        zcoordiante: float=None  
            The z-coordinate of the corner point.  
        dimensions: int=2  
            The dimension for which the distance is returned (either 2 or 3).  

        Returns.
        --------
        distance: float  
            The distance to the origin in millimeters.  
        '''
        if dimensions==3:
            if zcoordinate is None: raise ValueError("no z-coordinate given")
            else: return np.sqrt(np.square(cornerpoint[0])+np.square(cornerpoint[1])+np.square(zcoordinate))

        elif dimensions==2:
            return np.sqrt(np.square(cornerpoint[0])+np.square(cornerpoint[1]))
        
        else: raise ValueError("dimensions must be in {2,3}!")


    def __extractCornerPointsFromEnvironmentInfo(self, cornerpointinfo:dict) -> list:
        '''
        This method extracts the corner points from the corner point information the environment returns in step.  

        Parameters.
        -----------
        cornerpointinfo: dict  
            The part of the environment information that holds the corner point information.  

        Returns.
        --------
        possibleCornerPoints: list  
            A list of all corner points extended by the item orientation in this point.  

        Examples.
        ---------
        >>> cornerpointinfo
        {'ice cream in tub-00104737': {0: [(0, 0, 0)], 1: [(0, 0, 0)]}}

        >>> possibleCornerPoints
        [[0, 0, 0, 0], [0, 0, 0, 1]]
        '''
        # create a list of "extended" corner points with [x,y,z,orientation]
        possibleCornerPoints = []
        for orientationCornerPoints in cornerpointinfo.values():
            for orientation, cpointList in orientationCornerPoints.items():
                for corner in cpointList:
                    possibleCornerPoints.append(list(corner)+[orientation])

        return possibleCornerPoints


    def __estimateCurrentCPScoreWithUpcomingItems(self, info:dict, observation:np.ndarray) -> list:
        '''
        This method estimates the score of each corner point in the given list of corner points. Depending on the amount of CPUs on the running device, the list of corner points might be cropped to increase the performance.  

        Parameters.
        -----------
        cornerpoints: list  
            Lit of cornerpoints that are sorted with respect to the selected score.  
        info: dict  
            Additional information about the palletizing environment, which is obtained by the `step` method.  

        Notes.
        ------
        - Following [https://stackoverflow.com/questions/6976372/mulitprocess-pools-with-different-functions].  

        Examples.
        ---------
        >>> cornerpoints  
        [[0, 0, 0, 0], [0, 0, 0, 1]]  
        >>> info  
        {'all_orders_considered': False, 'allowed_area': {0: array([[1, 1, 1, ..., 0, 0, 0],
        [1, 1, 1, ..., 0, 0, 0],
        [1, 1, 1, ..., 0, 0, 0],
        ...,
        [0, 0, 0, ..., 0, 0, 0],
        [0, 0, 0, ..., 0, 0, 0],
        [0, 0, 0, ..., 0, 0, 0]]), 1: array([[1, 1, 1, ..., 0, 0, 0],
        [1, 1, 1, ..., 0, 0, 0],
        [1, 1, 1, ..., 0, 0, 0],
        ...,
        [0, 0, 0, ..., 0, 0, 0],
        [0, 0, 0, ..., 0, 0, 0],
        [0, 0, 0, ..., 0, 0, 0]])}, 'order_id': '00100010', 'palletizing_target': 'euro-pallet', 'next_items_selection': [{...}], 'next_items_preview': [{...}, {...}], 'n_items_in_order': 49, 'corner_points': {'salmon-00107470': {...}}}
        >>> estimatedScores  
        [{'initial_action': {...}, 'max_score': -0.8483328405274684, 'max_score_corner_point': [...]}, {'initial_action': {...}, 'max_score': -0.8483328405274684, 'max_score_corner_point': [...]}]  
        '''
        # prepare actions depending on items that can be selected
        collectionActionAndScore = []
        for item in info.get("next_items_selection", []):
            itemArticle = item.get("article")
            itemSize = item.get("length/mm"), item.get("width/mm"), item.get("height/mm")
            itemCP = info["corner_points"].get(itemArticle, {})

            for itemOrientation, listPossibleCPs in itemCP.items():
                if len(listPossibleCPs):
                    possibleCP = [list(cp)+[itemOrientation] for cp in listPossibleCPs]
                    possibleCP = self.__checkWhetherCornerPointsHaveToMoveOutwards(possibleCP, itemSize, observation.shape)
                    weightScoresCornerPoints = [self.__getScoreWeightsOfCornerPoint(observation, cp, itemSize) for cp in possibleCP]
                    scoresCornerPoints = self.FUNC_VECTORSCOREEVAL(weightScoresCornerPoints, self.__SCORE_WEIGHTS)
                    collectionActionAndScore += [{"actions": [{"x": cp[0], "y": cp[1], "orientation": cp[-1], "item": item}], "scores": [cpScore]} for cp, cpScore in zip(possibleCP,list(scoresCornerPoints))]

        # HERE STARTS THE SCORE ESTIMATION
        for nPreviewStep in range(self.__NPreview-1):
            if LIMIT_COMBINATIONS_AMOUNT:
                collectionActionAndScore.sort(key=lambda el: np.sum(el["scores"]), reverse=True)
                collectionActionAndScore = collectionActionAndScore[:N_LIMIT_COMBINATIONS]
                actionsForEstimation = [collEntry["actions"] for collEntry in collectionActionAndScore]
                templateSimEnv = copy.deepcopy(self.__SimEnvironment)
                templateSimEnv.remStoredOrder()
                mpEnvs = [copy.deepcopy(templateSimEnv) for _ in actionsForEstimation]
                actionsForEstimation = [(env, action) for env, action in zip(mpEnvs, actionsForEstimation)]
            
            else:
                # we need all actions that should be estimated
                actionsForEstimation = [collEntry["actions"] for collEntry in collectionActionAndScore]
                templateSimEnv = copy.deepcopy(self.__SimEnvironment)
                templateSimEnv.remStoredOrder()
                mpEnvs = [copy.deepcopy(templateSimEnv) for _ in actionsForEstimation]
                actionsForEstimation = [(env, action) for env, action in zip(mpEnvs, actionsForEstimation)]

            self.__MPStepInfo = {
                "next_items_selection": info.get("next_items_selection"),
                "next_items_preview": info.get("next_items_preview")
            }

            # startTime = time.time()
            # # ==================================================
            # with multiprocessing.Pool(processes=4) as pool:
            #     startMap = time.time()
            #     resultingCornerPointsForEstimation = pool.starmap(self.mpStepSimulation, actionsForEstimation, MULTI_PROCESSING_CHUNKSIZE)
            #     print(f"\tpool.map | finished {round((time.time()-startMap)*1000)} ms")
            # # ==================================================
            # print(f"mp.pool CALL & Return | mp finished {round((time.time()-startTime)*1000)} ms\n==========")
            # startTime = time.time()
            resultingCornerPointsForEstimation = [self.mpStepSimulation(*entry) for entry in actionsForEstimation]
            # logger.info(f"est. for {len(collectionActionAndScore)} combinations took {round((time.time()-startTime)*1000)} ms")
            
            # free memory
            del actionsForEstimation
            del mpEnvs

            tempCollectionActionsAndScores = []
            for i_cp, cpResults in enumerate(resultingCornerPointsForEstimation):
                # cpResults is a dict with keys "n_resulting_corner_points", "resulting_actions", and "scores" and used_item_for_scores
                #                                   int                             list of dicts               list     dict  
                for resAction, resCPScore in zip(cpResults["resulting_actions"], cpResults["scores"]):
                    # if actions were determined, add them to the possible combinations
                    tempInitCollEntry = copy.deepcopy(collectionActionAndScore[i_cp]) # need deepcopy since otherwise .append() changes the orig dict
                    
                    tempInitCollEntry["scores"].append(resCPScore)
                    tempInitCollEntry["actions"].append(resAction)
                
                    tempCollectionActionsAndScores.append(tempInitCollEntry)

            if tempCollectionActionsAndScores==[]: break
            collectionActionAndScore = tempCollectionActionsAndScores

        # TAKE THE ACTION WITH THE HIGHEST SCORE!
        collectionScores = [np.sum(collEntry["scores"]) for collEntry in collectionActionAndScore]
        maxScoreIndex = np.argmax(collectionScores)

        maxScoreAction = collectionActionAndScore[maxScoreIndex]["actions"][0]
        print(f"use {maxScoreIndex}.-action: \n==========\n{maxScoreAction}\n==========\n")

        # free memory
        del tempCollectionActionsAndScores
        gc.collect()
        return maxScoreAction


    def mpStepSimulation(self, dcSimEnv:"environment.SimPalEnv", stepactions: list) -> dict:
        '''
        We make the steps that are given. After doing these actions, we return a dictionary that holds the information about each step.  

        Parameters.
        -----------
        dcSimEnv: `environment.SimPalEnv`  
            A deepcopy of the template self.__SimEnvironment.  
        stepactions: list  
            All step actions that are required to create the actual state of the environment, starting from the stored template state.
        
        Returns.
        --------
        returnInformation: dict  
            Holds information about the resulting corner points and their scores.  
        '''
        returnInformation = {
            "n_resulting_corner_points": 0,
            "resulting_corner_points": None,
            "scores": None
        }
        dcSimEnv.setItems(preview=self.__MPStepInfo.get("next_items_preview"), selection=self.__MPStepInfo.get("next_items_selection"))
        for action in stepactions:
            newObservation, _, done, nextInfo = dcSimEnv.step(action)
            if done: break


        possibleCP = self.__extractCornerPointsFromEnvironmentInfo(nextInfo.get("corner_points", {}))
        if possibleCP==[]: 
            returnInformation["resulting_actions"] = []
            returnInformation["resulting_corner_points"] = []
            returnInformation["scores"] = []

        else:
            nextItem = nextInfo["next_items_selection"][0]
            nextItemSize = [nextItem["length/mm"], nextItem["width/mm"], nextItem["height/mm"]]

            # Calculate the scores of the corner points
            possibleCP = self.__checkWhetherCornerPointsHaveToMoveOutwards(possibleCP, nextItemSize, newObservation.shape)
            weightScoresCornerPoints = [self.__getScoreWeightsOfCornerPoint(newObservation, cp, nextItemSize) for cp in possibleCP]
            scoresCornerPoints = self.FUNC_VECTORSCOREEVAL(weightScoresCornerPoints, self.__SCORE_WEIGHTS)

            
            returnInformation["n_resulting_corner_points"] = len(possibleCP)
            returnInformation["resulting_corner_points"] = possibleCP
            returnInformation["scores"] = scoresCornerPoints
            returnInformation["used_item_for_scores"] = nextItem

            # resulting actions
            returnInformation["resulting_actions"] = [self.__convertCornerPointToAction(cp[:3], nextItem, cp[-1]) for cp in possibleCP]

        return returnInformation


    def __convertCornerPointToAction(self, cornerpoint:list, item:dict, itemorientation:int) -> dict:
        '''
        Converts a corner point to an action for the palletizing environment.  

        Parameters.
        -----------
        cornerpoint: list  
            The coordinates of the corner point.  
        item: dict  
            The item dictionary.  
        itemorientation: int  
            The orientation of the item.  
        
        Returns.
        --------
        action: dict  
            The resulting action for the environment.  
        '''
        action = {
            "x": cornerpoint[0],
            "y": cornerpoint[1],
            "orientation": itemorientation,
            "item": item
        }
        return action


    def __checkWhetherCornerPointsHaveToMoveOutwards(self, cornerpoints:list, itemSize:list, observationshape:tuple) -> list:
        '''Change inline the x- and y-coordinate of the conerpoints and return the list of adapted corner points.'''
        targetLenY, targetLenX = observationshape

        for cp in cornerpoints:
            itemOrientation = cp[-1]

            if itemOrientation==0:   deltaX, deltaY = itemSize[0], itemSize[1]
            elif itemOrientation==1: deltaX, deltaY = itemSize[1], itemSize[1]

            if cp[0]+deltaX >= 0.75*targetLenX:
                # move x-coordinate towards outside
                cp[0] = int(0.9*targetLenX-deltaX)
            if cp[1]+deltaY >= 0.75*targetLenY:
                # move y-coordiante towards outside
                cp[1] = int(0.9*targetLenY-deltaY)
            
        return cornerpoints

