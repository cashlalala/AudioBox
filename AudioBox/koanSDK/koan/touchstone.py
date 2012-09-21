import time
import os
import platform

################################################
#   touch stone
################################################

touchstone          = True     # enable touchstone?
tsScript            = None     # touchstone recording mode (None: stop, number : recording mode)
lastTime            = 0
recordTime          = False

def startTSRecording():
    global tsScript, lastTime, recordTime
    if tsScript is None:   
        t = time.localtime()
        fp = platform.reg.GetRegistry("TSScriptPath", r"c:\\")
        recordTime = platform.reg.GetRegistry("TSRecordTime", False)
        fn = str(t[0])+"_"+str(t[1])+str(t[2])+"_"+str(t[3])+str(t[4])+".ts"
        tsScript = os.open(os.path.join(fp, fn), os.O_WRONLY | os.O_CREAT)
        lastTime = time.time()

def recordActivateCmd(name):
    if name is not None:
        cmd = "activate('%s')" %name
        recordTSCmd(cmd)

def recordKeyinCmd(name):
    if name is not None:
        cmd = "keyin('%s')" %name
        recordTSCmd(cmd)
        
def recordCommand(name):
    if name is not None:
        cmd = "command('%s')" %name
        recordTSCmd(cmd)
        
def recordTSCmd(cmd, timing = True):
    global tsScript, lastTime, recordTime
    if tsScript is not None:
        if timing and recordTime:
            t = time.time()
            elapseTime = t - lastTime
            lastTime = t
            os.write( tsScript, cmd + ";\t\tsleep(%f)" %elapseTime + "\n")
        else:
            os.write( tsScript, cmd + "\n")
        print "############# touch stone ############## ", cmd
    pass
        
def recordComment(name):
    if name is not None:
        cmd = "# %s\n" %name
        recordTSCmd(cmd, False)
    
def stopTSRecording():    
    global tsScript
    if tsScript is not None:
        os.close(tsScript)
        tsScript = None

