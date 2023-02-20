'''
This module provides a class which represents a virtual load carrier.
'''


class LC:
    '''
    Objects of this class represent represent different load carriers.
    '''
    def __init__(self, props:dict) -> None:
        self.__ID = props['cont_id']
        '''The id of the object.'''
        
        self.__SKU = props.get("sku", "")
        '''The SKU of the object.'''
        self.__LCType = props.get("lc_type", "None")
        '''The type of the object.'''


        self.__Length = int(props.get("length", 0))
        '''The object's length in millimeters.'''
        self.__Width = int(props.get("width", 0))
        '''The object's width in millimeters.'''
        self.__Height = int(props.get("height", 0))
        '''The object's height in millimeters.'''

        self.__Weight = props.get("weight", 0.0)
        '''The object's weight in kilogramm.'''
        

        self.__Targetposition = {
            'area': None, 
            'x': 0, # on target
            'y': 0, # on target
            'z': 0 # on target
        }
        '''The position of the load carrier on a target.'''


    def getProperties(self) -> dict:
        '''Returns the properties of the load carrier as dictionary.'''
        length, width, height = self.getDimensions()
        lcProps = {
            "cont_id": self.getID(),
            "sku": self.getSKU(),
            "lc_type": self.getLCType(),
            "length": length,
            "width": width,
            "height": height,
            "weigth": self.getWeight(),
            "target_pos": self.getTargetposition()
        }
        return lcProps


    def getLCType(self) -> str:
        '''Returns the load carrier type.'''
        return self.__LCType


    def getID(self) -> str:
        '''Returns the load carrier's ID number.'''
        return self.__ID


    def getHeight(self) -> int:
        '''Returns the height of the load carrier.'''
        return self.__Height


    def getWeight(self) -> float:
        '''Returns the weight of the load carrier.'''
        return self.__Weight


    def getSKU(self) -> str:
        '''Returns the SKU of the load carrier.'''
        return self.__SKU


    def getDimensions(self) -> list:
        '''Returns the length, width and height of the load carrier as a list.'''
        return [self.__Length, self.__Width, self.__Height].copy()


    def getTargetposition(self, coordinate=None):
        '''
        Returns the target position of the load carrier. If the parameter `coordinate` is specfied, the requested coordinate is returned.  

        Parameters.
        -----------
        coordinate: str (default: None)  
            Possible values are "x", "y", "z" and "area".  

        Returns.
        --------
        target: dict  
            The target position of the object, i.e., a dictionary with the keys 'area', 'x', 'y' and 'z'.  
        OR
        coordinate: int  
            The requested coordinate.  
        '''
        if coordinate is None:
            # return a copy of the targetposition coordinates
            return self.__Targetposition.copy()
        else:
            # return the specified coordinate
            return self.__Targetposition.copy()[coordinate]


    def getVolume(self) -> float:
        '''Calculates the volume of the LC in [mm^3] and returns it as float.'''
        return float(self.__Length * self.__Width * self.__Height)


    def setTargetposition(self, target:dict) -> None:
        '''
        Sets the targetposition of the load carrier.  
        
        Parameters.
        -----------
        target: dict
            The target position of the object, i.e., a dictionary with the keys 'area', 'x', 'y' and 'z'.  
        '''		
        self.__Targetposition['area'] = target['area']
        self.__Targetposition['x'] = target['x']
        self.__Targetposition['y'] = target['y']
        self.__Targetposition['z'] = target['z']
