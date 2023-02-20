'''
This module contains a class that represents a virtual, three-dimensional space.  
'''
import environment
from environment import HEIGHT_TOLERANCE_MM as HEIGHT_TOLERANCE_MM
import numpy as np
import logging
import utils

logger = logging.getLogger(__name__)

MAXHEIGHT = 3000 # for corner points
'''The maximum height in millimeters for that corner points are determined. Needs to be greater than the maximum palletizing height.'''


class Space3D():
    '''
    This class represents a virtual space to which items are added.  
    describe class Space3D

    Parameters.
    -----------
    basesize: tuple (default = (1200, 800))  
        The space's size of the base area in x- and y-direction given in millimeters.  

    Attributes.
    -----------
    __Heights: np.ndarray  
        'This `np.ndarray` has the shape of the palletizing target and stores the height in each position in millimeters.  
    __PlacedItems: dict  
        This dictionary's keys are the chronological order of the placed items and its values are the items as `"environment.Item3D"` object.  
    __Size: tuple  
       The space's size of the base area in x- and y-direction given in millimeters.  
    __UppermostItems:  np.ndarray  
        This `np.ndarray` has the same shape as the height map of the three-dimensional space and stores a counter that represents the counter of the uppermost item.  
    '''
    def __init__(self, basesize:tuple = (1200, 800)) -> None:
        self.__Size = basesize
        '''The space's size of the base area in x- and y-direction given in millimeters.'''

        self.__PlacedItems = {}
        '''This dictionary's keys are the chronological order of the placed items and its values are the items as `"environment.Item3D"` object.'''

        targetShape = self.__Size[1], self.__Size[0]
        self.__Heights = np.zeros(targetShape, dtype=int)
        '''This `np.ndarray` has the shape of the palletizing target and stores the height in each position in millimeters.'''

        self.__UppermostItems = np.zeros(targetShape, dtype=int)
        '''This `np.ndarray` has the same shape as the height map of the three-dimensional space and stores a counter that represents the counter of the uppermost item.'''


    def getPlacedItems(self) -> list:
        '''Returns all placed items as list of "environment.Item3D".'''
        return list(self.__PlacedItems.values())


    def addItem(self, item:"environment.Item3D", orientation:int, flbcoordinates:list) -> None:
        '''
        Adds an item to the virtual three-dimensional space and calculates the required attributes for the stability check evaluation.

        Parameters.
        -----------
        item: "environment.Item3D"
            The item that is added to the space.  
        orientation: int
            The orientation of the item.  
        flbcoordinates: list
            The FLB coordinates in which the item is placed.  
        '''
        item.storeFLBCoordinates(flbcoordinates)
        itemArray = item.getRepresentation()
        # define the area where the item is located
        startX, startY = flbcoordinates[0], flbcoordinates[1]
        deltaX, deltaY = itemArray.shape[1], itemArray.shape[0]
        endX, endY = startX+deltaX, startY+deltaY

        # detect all items that directly support the current item
        itemsAreaBelow = self.__UppermostItems[startY:endY, startX:endX]
        heightsAreaBelow = self.__Heights[startY:endY, startX:endX]
        heightThreshold = flbcoordinates[2]-HEIGHT_TOLERANCE_MM
        itemsWithDirectSupport = np.where(heightsAreaBelow>=heightThreshold, itemsAreaBelow, -1)
        allItemsBelow = np.unique(itemsWithDirectSupport)
        # remove item counter 0 <=> palletizing target 
        # needed condition item <= len(placed items) because strange errors sometimes occured during dev
        countersDirectItemsBelow = [item for item in allItemsBelow if ((item>0) and (item <=len(self.__PlacedItems)))]
        # obtain the Item3D objects and store it in the current item
        itemsDirectlyBelow = [self.__PlacedItems[countItem] for countItem in countersDirectItemsBelow]
        item.storeItemsDirectlyBelow(itemsDirectlyBelow)

        # detect all neighbors of the current item
        targetSizeY, targetSizeX = self.__UppermostItems.shape
        neighborStartX = startX if startX==0 else startX-1
        neighborEndX = endX if endX==targetSizeX-1 else endX+1
        neighborStartY = startY if startY==0 else startY-1
        neighborEndY = endY if endY==targetSizeY-1 else endY+1
        # create np.ndarray with items and heights
        itemsAreaNeighbor = self.__UppermostItems[neighborStartY:neighborEndY, neighborStartX:neighborEndX]
        heightsAreaNeighbor = self.__Heights[neighborStartY:neighborEndY, neighborStartX:neighborEndX]

        heightThreshold = flbcoordinates[2]#-HEIGHT_TOLERANCE_MM
        itemsSurround = np.where(heightsAreaNeighbor>heightThreshold, itemsAreaNeighbor, -1)
        allItemsSurround = np.unique(itemsSurround)
        # # remove item counter 0 <=> palletizing target
        countersPossibleNeighborItems = [item for item in allItemsSurround if item>0 and not(item in itemsDirectlyBelow)]
        # # obtain the Item3D objects and store it in the current item
        possibleNeighbors = [self.__PlacedItems[countItem] for countItem in countersPossibleNeighborItems]
        self.__identifyNeighbors(item, possibleNeighbors)


        # update the heights attribute
        crop = ""
        if endX-startX > self.__Heights.shape[1]-startX:
            logger.warning("crop item in X direction")
            endX = self.__Heights.shape[1]
            crop += "x"
        if endY-startY > self.__Heights.shape[0]-startY:
            logger.warning("crop item in Y direction")
            endY = self.__Heights.shape[0]
            crop += "y"
        self.__Heights[startY:endY, startX:endX] = flbcoordinates[2] * np.ones((endY-startY, endX-startX), dtype=int)
        self.__Heights[startY:endY, startX:endX] += itemArray[:endY-startY, :endX-startX]

        # update the uppermost items attribute and the placed items
        counterItem = len(self.__PlacedItems)+1
        self.__UppermostItems[startY:endY, startX:endX] = counterItem * np.ones((endY-startY, endX-startX), dtype=int)
        self.__PlacedItems[counterItem] = item


    def reset(self, basesize:tuple) -> None:
        '''
        Resets the attributes to their initial values and reshapes the numpy.ndarrays that store the heights and uppermost items.    

        Parameters.
        -----------
        basesize: tuple     
            The shape of the base area given as `(shape_x, shape_y)`.     
        '''
        self.__Size = basesize
        targetShape = self.__Size[1], self.__Size[0]

        self.__PlacedItems = {}
        self.__Heights = np.zeros(targetShape, dtype=int)
        self.__UppermostItems = np.zeros(targetShape, dtype=int)


    def getHeights(self) -> np.ndarray:
        '''Returns the heights in millimeters in each coordinate of the space.'''
        return self.__Heights


    def getItemsAboveHeightLevel(self, heightlevel: int) -> int:
        '''
        Returns the amount of items that are located above the given height.  

        Parameters.
        -----------
        heightlevel: int  
            The height on the target in millimeters for that defines which items are counted as unpalletized.  
        
        Returns.
        --------
        nItemsAboutHLevel: int  
            The items that are located above a certain height level.  
        '''
        nItemsAboutHLevel = 0
        for item in self.getPlacedItems():
            if min(item.getCoordinatesHeightRange()) > heightlevel:
                nItemsAboutHLevel += 1

        return nItemsAboutHLevel


    def getMaximumHeightBelowHeightLevel(self, heightlevel:int) -> int:
        '''
        Returns the maximum height of the target for which the items are completely below the given heightlevel.  

        Parameters.
        -----------
        heightlevel: int  
            The height on the target in millimeters for that defines which items are counted as unpalletized.  

        Returns.
        --------
        maxTargetHeight: int  
            The maximum target height below a given height level in millimeters.
        '''
        maxTargetHeight = 0
        for item in self.getPlacedItems():
            itemZLocation = max(item.getCoordinatesHeightRange())
            if itemZLocation > maxTargetHeight and itemZLocation <= heightlevel:
                maxTargetHeight = itemZLocation

        return maxTargetHeight


    def __identifyNeighbors(self, item: "environment.Item3D", possibleneighbors:list) -> None:
        '''
        Identifies the neighbors of the given item and stores the neighbors of item in the object.  

        This method checks  
        (1) whether the item is located next to an item in the possible neighbors.  
        (2) The top of a possible neighbor item has to be in the height range of given item.  
        (3) If (2) is satisfied, we have to check whether the items below the possible neighbor are neighbors as well.  
        (4) If (2) is not satisfied, we know that neither the possible neighbor, nor the items below are neighbors.
        
        Parameters.
        -----------
        item: "environment.Item3D"  
            The item for which the neighbors are identified.  
        possibleneighbors: list (of "environment.Item3D" objects)  
            Items that could be neighbors of item.          
        '''
        EDGES_TO_COMPARE = {
            0: ["north", "south"],
            1: ["east", "west"],
            2: ["south", "north"],
            3: ["west", "east"]
        }
        '''Holds the combination of the edges that have to be compared, formatted as [edge_of_item, edge_of_possible_neighbor]'''
        
        identifiedNeighbors = {
            "north": [],
            "east": [],
            "south": [],
            "west": []
        }
        
        allItemsInvestigated = possibleneighbors == []

        while not(allItemsInvestigated):
            neighborToInvestigate = possibleneighbors.pop(0)
            
            for edgeItem, edgePNeighbor in EDGES_TO_COMPARE.values():
                itemEdge = item.getCoordinatesEdge(edgeItem)
                pneighborEdge = neighborToInvestigate.getCoordinatesEdge(edgePNeighbor)

                xIntersection, yIntersection = set.intersection(itemEdge["x"], pneighborEdge["x"]), set.intersection(itemEdge["y"], pneighborEdge["y"])

                if len(xIntersection) and len(yIntersection):
                    # neighbors in x-y-direction
                    # make height check
                    itemOccupiedHeight = item.getCoordinatesHeightRange()
                    pneighborOccupiedHeight = neighborToInvestigate.getCoordinatesHeightRange()

                    zIntersection = set.intersection(itemOccupiedHeight, pneighborOccupiedHeight)
                    heightCheckSuccessful = len(zIntersection) > 0

                    if heightCheckSuccessful:
                        identifiedNeighbors[edgeItem].append(neighborToInvestigate)
                    
                    # investigate items below when min height of item less than highest point of possible neighbor
                    if min(itemOccupiedHeight) < max(pneighborOccupiedHeight):
                        possibleneighbors += neighborToInvestigate.getItemsBelow()
                        # remove duplicates
                        possibleneighbors = list(set(possibleneighbors))

            allItemsInvestigated = possibleneighbors == []

        item.storeNeighbors(identifiedNeighbors)


    def getCornerPointsIn3D(self, itemdimension:tuple=(0,0,0)) -> list:
        '''
        Determines the corner points of the placed items and returns them. The corner points are calculated like described in the algorithms `2D-CORNERS` and `3D-CORNERS` in (Martello et al, 2000).  

        Parameters.
        -----------
        itemdimensions: tuple  
            The length, width, and height of an item for which the corner points are calculated.  

        Returns.
        --------
        threeDimCornerPoints: list  
            The corner points for an item that has the given dimension.  
        '''
        placedItems = self.getPlacedItems()
        if placedItems==[]:
            return [(0, 0, 0)]

        # create a list of height levels 
        targetHeightLevels = [0] + list(set([item.getFLBCoordinates()[2] + item.getHeight() for item in placedItems]))
        targetHeightLevels.sort()

        threeDimCornerPoints = []
        prev2DCornerPoints = []

        for heightValue in targetHeightLevels:
            # stop search if first time a placement would exceed the maximum height
            if heightValue + itemdimension[2] > MAXHEIGHT: break

            # create a subset of placed items that are located above the height level
            I_k = [item for item in placedItems if ((item.getFLBCoordinates()[2] + item.getHeight())>heightValue)]

            # search for corner points in 2D
            twoDimCornerPoints = self.__get2DCorners(I_k, itemdimension[0:2])
            
            # check for true corner points
            for cornerPoint in twoDimCornerPoints:
                if not(cornerPoint in prev2DCornerPoints):
                    # create corner point in 3D
                    cornerPoint3D = cornerPoint + (heightValue,) 
                    threeDimCornerPoints.append(cornerPoint3D)

            # update prev2DCornerPoints
            prev2DCornerPoints = twoDimCornerPoints

        return threeDimCornerPoints


    def __get2DCorners(self, placeditems: list, itemdimension:tuple) -> list:
        '''
        Determines the corner points of the placed items and returns them. The corner points are calculated like described in the algorithm `2D-CORNERS` in (Martello et al, 2000).  

        Parameters.
        -----------
        placeditems: list  
            List of items that are placed in the 2D area.  
        itemdimension: 2-tuple  
            The length and width of an item for which the corner points are calculated.  

        Returns.
        --------
        twoDimCornerPoints: list  
            The corner points for an item that has the given dimension.  
        '''
        def __getEndpointYthenX(item:"environment.Item3D") -> tuple:
            '''Returns the endpoint of the item as (y, x).'''
            xCoordinate, yCoordinate, _ = item.getFLBCoordinates()
            deltaY, deltaX = item.getRepresentation().shape
            return (yCoordinate+deltaY, xCoordinate+deltaX)
            
        if placeditems==[]:
            return [(0, 0)]

        # sort placeditems
        placeditems.sort(key=__getEndpointYthenX, reverse=True)

        # determine extreme points
        itemsForExtremePoints = []
        maxXValue = 0
        for item in placeditems:
            valEndpointX = item.getFLBCoordinates()[0] + item.getRepresentation().shape[1] 
            if (valEndpointX) > maxXValue:
                itemsForExtremePoints.append(item)
                maxXValue = valEndpointX

        # determine coordinates of corner points
        nExtremePoints = len(itemsForExtremePoints)
        twoDimCornerPoints = []
        firstCandiate = itemsForExtremePoints.pop(0)
        prevX = firstCandiate.getFLBCoordinates()[0] + firstCandiate.getRepresentation().shape[1]
        prevY = firstCandiate.getFLBCoordinates()[1] + firstCandiate.getRepresentation().shape[0]
        twoDimCornerPoints.append((0, prevY))

        if nExtremePoints>1:
            lastCandiate = itemsForExtremePoints.pop()
            lastX = lastCandiate.getFLBCoordinates()[0] + lastCandiate.getRepresentation().shape[1]

            for candidate in itemsForExtremePoints:
                candX = candidate.getFLBCoordinates()[0] + candidate.getRepresentation().shape[1]
                candY = candidate.getFLBCoordinates()[1] + candidate.getRepresentation().shape[0]

                twoDimCornerPoints.append((prevX, candY))
                prevX = candX
        else:
            lastX = prevX
        twoDimCornerPoints.append((lastX, 0))

        # remove infeasible corner points
        for cornerPoint in twoDimCornerPoints.copy():
            if (cornerPoint[0]+itemdimension[0] > self.__Size[0]) or (cornerPoint[1]+itemdimension[1] > self.__Size[1]):
                twoDimCornerPoints.remove(cornerPoint)


        return twoDimCornerPoints
