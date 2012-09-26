@echo off
@echo.

@set curPath=%~dp0
@echo current batch file is at %curPath%

@echo Starting build... 

@echo setting  python path...  
@set PATH=C:\python\python25

@echo get into pyinstaller...
@E:
@cd E:\pyinstaller-2.0

@python pyinstaller.py --paths="%curPath%AudioBox\koanSDK";"%curPath%Debug";"%curPath%AudioBox" --onefile -o "%USERPROFILE%\Desktop\Ouput" "%curPath%AudioBox\AudioBox.py" 

@echo output the generated folder to %USERPROFILE%\Desktop\Ouput

@copy "%curPath%AudioBox\dsplayer.xml" "%USERPROFILE%\Desktop\Ouput\dist"