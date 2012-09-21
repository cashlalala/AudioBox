from comp.PlayerWindow import PlayerWindow
from Widgets.kxmlparser import loadKXML
import koan

if __name__ == '__main__':   
      
    koan.init();
        
    w = PlayerWindow()    
    loadKXML(w, sys.argv[1])
    w.show()
        
    koan.run(1)
    koan.final()
    
    
    pass

