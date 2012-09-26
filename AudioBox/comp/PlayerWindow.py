'''
Created on 2012/9/19

@author: Cash_Chang
'''
from Widgets.window import Window
import DSPlayer
import logging
import sys
#from Widgets.button import TextButton
#from Widgets.text import Text
#from ctypes import create_string_buffer

class PlayerWindow(Window):
    '''
    classdocs
    '''

    def __init__(self):
        """
        window init 
        """
        Window.__init__(self)       
        self.create(0, 0, 400, 150, caption=True)
        self.dsPlayer = DSPlayer.CreateDSPlayerObject()
        self.statusText = ""
        self.fileName = None
        
        """
        logger setting 
        """
        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console = logging.StreamHandler()    
        console.setLevel(logging.DEBUG)    
        console.setFormatter(formatter)
        
        fileHandler = logging.FileHandler("honoiText.log", mode='w')
        fileHandler.setFormatter(formatter)
        
        
        self.logger.addHandler(console)
        self.logger.addHandler(fileHandler)
        self.logger.setLevel(logging.DEBUG)
        
        
    def __del__(self):
        DSPlayer.DeleteDSPlayerObject(self.dsPlayer)
        Window.__del__(self)
  
    def onClickOpenFile(self):
        try:
            result = self.dsPlayer.OpenFileDialog()
            self.logger.debug("open file dialog result: %d" , result)
            tmpFileName = DSPlayer.GetFileName(self.dsPlayer)
            self.logger.debug(tmpFileName)
            if tmpFileName != None and len(tmpFileName) != 0:
                self.fileName = str(tmpFileName).rsplit('\\')[-1]
                self.statusText = "Selected...\n" + self.fileName
            else:
                self.logger.debug("user canceled")
        except:
            etype, message, traceback = sys.exc_info()
            while traceback:
                self.logger.debug('..........')
                self.logger.debug(etype)
                self.logger.debug(message)
                self.logger.debug('function or module? %s', traceback.tb_frame.f_code.co_name)
                self.logger.debug('file? %s', traceback.tb_frame.f_code.co_filename)
                traceback = traceback.tb_next

    def onClickPlay(self):
        if self.fileName != None and len(self.fileName) != 0:
            self.dsPlayer.DoPlay()
            self.statusText = "Now Playing...\n" + self.fileName
        
    def onClickStop(self):
        if self.fileName != None and len(self.fileName) != 0:
            self.dsPlayer.DoStop()
            self.statusText = "Stop...\n" + self.fileName
        
    def onClickPlayOrPause(self):
        if self.fileName != None and len(self.fileName) != 0:
            if self.dsPlayer.GetIsPlaying():
                self.statusText = "Pause...\n" + self.fileName
            else:
                self.statusText = "Play...\n" + self.fileName
            self.dsPlayer.DoPlayOrPause()

        
        
        
