@echo off
REM Because MS can't get their shit together for reasonable
REM command line builds without setting all kinds of environment
REM variables.

if [%1]==[] (
	set /p VERS=Version number?: 
) else (
	set VERS=%1
)

set OLDDIR=%CD%
cd C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin
CALL vcvars32.bat
chdir /d %OLDDIR%
python angel_samples_win.py %VERS%

