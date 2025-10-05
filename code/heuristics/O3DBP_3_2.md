## Integration of Heuristic O3DBP-3-2

For the paper we used the following implementation of `O3DBP-3-2`.

### Source Code
```python
import copy
import bed_bpp_env.environment.SimPalEnv
import logging
import numpy as np
import os
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
    The used weights are [1.3, -2.0, -1.00001, -1.2].
    '''
    def __init__(self, preview:int=3, selection:int=2) -> None:
        self.__SimEnvironment = None
        self.__NPreview = preview
        self.__NSelection = selection
        self.__SCORE_WEIGHTS = [1.3, -2.0, -1.00001, -1.2]
        self.FUNC_VECTORSCOREEVAL = np.vectorize(self.multiplyWeightScore, excluded=[1], signature="(n)->()")

    def setSimEnv(self, environment:"environment.SimPalEnv") -> None:
        self.__SimEnvironment = environment


    def getAction(self, observation:np.ndarray, info:dict) -> Tuple[dict, bool]:
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


    def __estimatePlacementZCoordinate(self, observation:np.ndarray, cornerpoint: list, itemsize: list) -> int:
        cpXCoord, cpYCoord = cornerpoint[0], cornerpoint[1]
        itemOrientation = cornerpoint[-1]

        if itemOrientation==0:
            deltaX, deltaY = int(itemsize[0]), int(itemsize[1])
        elif itemOrientation==1:
            deltaX, deltaY = int(itemsize[1]), int(itemsize[0])

        estimatedHeight = np.amax(observation[cpYCoord:cpYCoord+deltaY, cpXCoord:cpXCoord+deltaX]) + itemsize[-1]
        return estimatedHeight


    def __estimateSupportArea(self, observation:np.ndarray, cornerpoint: list, itemsize: list) -> float:
        cpXCoord, cpYCoord = cornerpoint[0], cornerpoint[1]
        itemOrientation = cornerpoint[-1]

        if itemOrientation==0:
            deltaX, deltaY = int(itemsize[0]), int(itemsize[1])
        elif itemOrientation==1:
            deltaX, deltaY = int(itemsize[1]), int(itemsize[0])

        placementArea = observation[cpYCoord:cpYCoord+deltaY, cpXCoord:cpXCoord+deltaX]
        maxHeightPlacementArea = np.amax(placementArea)

        estimatedSuppArea = np.count_nonzero((placementArea > maxHeightPlacementArea-10) & (placementArea < maxHeightPlacementArea+10))/placementArea.size
        return estimatedSuppArea


    def __getDistanceToOrigin(self, cornerpoint:list, zcoordinate:float=None, dimensions:int=2) -> float:
        if dimensions==3:
            if zcoordinate is None: raise ValueError("no z-coordinate given")
            else: return np.sqrt(np.square(cornerpoint[0])+np.square(cornerpoint[1])+np.square(zcoordinate))

        elif dimensions==2:
            return np.sqrt(np.square(cornerpoint[0])+np.square(cornerpoint[1]))
        
        else: raise ValueError("dimensions must be in {2,3}!")


    def __extractCornerPointsFromEnvironmentInfo(self, cornerpointinfo:dict) -> list:
        # create a list of "extended" corner points with [x,y,z,orientation]
        possibleCornerPoints = []
        for orientationCornerPoints in cornerpointinfo.values():
            for orientation, cpointList in orientationCornerPoints.items():
                for corner in cpointList:
                    possibleCornerPoints.append(list(corner)+[orientation])

        return possibleCornerPoints


    def __estimateCurrentCPScoreWithUpcomingItems(self, info:dict, observation:np.ndarray) -> list:
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

        # check whether the height with this action in the origin is less than in action
        
        # free memory
        del tempCollectionActionsAndScores
        gc.collect()
        return maxScoreAction


    def mpStepSimulation(self, dcSimEnv:"environment.SimPalEnv", stepactions: list) -> dict:
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
        action = {
            "x": cornerpoint[0],
            "y": cornerpoint[1],
            "orientation": itemorientation,
            "item": item
        }

        return action


    def __getScoreWeightsOfCornerPoint(self, observation:np.ndarray, cornerpoint:list, itemsize:list) -> float:
        itemOrientation = cornerpoint[-1]

        estimatedSupportArea = self.__estimateSupportArea(observation, cornerpoint, itemsize)
        estimatedZCoordinate = self.__estimatePlacementZCoordinate(observation, cornerpoint, itemsize)
        
        distanceOrigin3D = self.__getDistanceToOrigin(cornerpoint, zcoordinate=estimatedZCoordinate, dimensions=3)
        # distanceOrigin2D = self.__getDistanceToOrigin(cornerpoint, dimensions=2)

        normedDistOrig3D = distanceOrigin3D/np.sqrt(np.square(observation.shape[0])+np.square(observation.shape[1])+np.square(2000))
        values = [estimatedSupportArea, estimatedZCoordinate/np.amax(observation, initial=estimatedZCoordinate), itemOrientation, normedDistOrig3D]
        return values


    def multiplyWeightScore(self, values:list, weights:list) -> float:
        if values.shape==(0,):
            # no values given
            values = [0]*len(weights)
        
        return np.dot(values, weights)


    def __checkWhetherCornerPointsHaveToMoveOutwards(self, cornerpoints:list, itemSize:list, observationshape:tuple) -> list:
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

```
