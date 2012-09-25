@echo off
@set curPath=%~dp0
@echo current batch file is at %curPath%
@call "%curPath%build_home.bat" > "%curPath%build_home.log.txt"