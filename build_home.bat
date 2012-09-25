@echo off
@echo.

@set curPath=%~dp0
@echo current batch file is at %curPath%

@echo Starting build... 

@echo setting  python path...  
@set PATH=C:\python\python25

@echo get into pyinstaller...
@D: 
@cd D:\Program Files\pyinstaller-2.0

@python pyinstaller.py --paths="%curPath%AudioBox\koanSDK";"%curPath%Debug";"%curPath%AudioBox" --onefile -o "%USERPROFILE%\Desktop\Ouput" "%curPath%AudioBox\AudioBox.py" 

@echo output the generated folder to %USERPROFILE%\Desktop\Ouput