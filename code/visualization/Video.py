'''
This module creates .mp4 videos from list of images.  
'''
import cv2
import logging
import os
import pathlib
import visualization	

logger = logging.getLogger(__name__)


class Video:
    '''
    This class creates.mp4 videos of the palletizing process. It uses images of the palletizing that are created during the item placements.  

    Parameters.
    -----------
    filename: str (default="video.mp4")  
        The filename of the created video.  

    Attributes.
    -----------
    __Filename: str
        The filename of the video.  
    __Outputfolder: pathlib.Path  
        The directory in which the video is stored.  
    '''
    def __init__(self, filename:str = "video.mp4") -> None:
        self.__Filename = filename 
        '''The filename of the video.'''
        self.__Outputfolder = visualization.OUTPUTDIRECTORY
        '''The folder in which the video is stored.'''
        

    def makeVideo(self, listOfImages) -> None:
        '''
        Creates a video from a given list of images. The video has the same size as an image.
        
        Parameters.
        -----------
            listOfImages: list
                A list which contains the images for the video.
        '''
        shape_x, shape_y = listOfImages[0].shape[1], listOfImages[0].shape[0]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        pathVideo = self.__Outputfolder
        if not os.path.exists(pathVideo):
            os.makedirs(pathVideo)

        videoname = pathlib.Path.joinpath(pathVideo, self.__Filename)
        videoname = videoname.as_posix()
        out = cv2.VideoWriter(videoname, fourcc, 4.0, (shape_x,shape_y))
        # iterate over the list of images
        for image in listOfImages:
            # write the images to a video
            out.write(image)
        # release the video
        out.release()

        logger.info(f"created video with {len(listOfImages)} images")
