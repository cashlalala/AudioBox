import koan
#from Widgets.window import Window
import DSPlayer

a = DSPlayer.CreateDSPlayerObject()
print a 
DSPlayer.DeleteDSPlayerObject(a)
koan.init()
w = Window(None)
w.show()
koan.run(1)
koan.final()

