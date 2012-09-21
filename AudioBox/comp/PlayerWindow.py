'''
Created on 2012/9/19

@author: Cash_Chang
'''
from Widgets.window import Window
import DSPlayer
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
        self.fileName = ""
        
        
    def __del__(self):
        DSPlayer.DeleteDSPlayerObject(self.dsPlayer)
        Window.__del__(self)
  
    def onClickOpenFile(self):
        self.dsPlayer.OpenFileDialog()
        self.fileName = str(DSPlayer.GetFileName(self.dsPlayer)).rsplit('\\')[-1]
        self.statusText = "Selected...\n" + self.fileName
#        self.txtBoxFile.text

    def onClickPlay(self):
        self.dsPlayer.DoPlay()
        self.statusText = "Now Playing...\n" + self.fileName
        
    def onClickStop(self):
        self.dsPlayer.DoStop()
        self.statusText = "Stop...\n" + self.fileName
        
    def onClickPlayOrPause(self):
        if self.dsPlayer.GetIsPlaying():
            self.statusText = "Pause...\n" + self.fileName
        else:
            self.statusText = "Play...\n" + self.fileName
        self.dsPlayer.DoPlayOrPause()

        
        
        