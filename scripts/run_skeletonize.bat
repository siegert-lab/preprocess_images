@echo off
REM Check if exactly two arguments (input and output folder paths) are provided
IF "%~2"=="" (
    echo Usage: %0 ^<input_folder^> ^<output_folder^>
    exit /b
)

REM Set input arguments
SET INPUT_FOLDER=%~1
SET OUTPUT_FOLDER=%~2

REM Define MATLAB executable path
SET MATLAB_PATH="C:\Program Files\MATLAB\R2022b\bin\matlab.exe"

REM Check if MATLAB executable exists
IF NOT EXIST %MATLAB_PATH% (
    echo MATLAB executable not found at %MATLAB_PATH%
    exit /b
)

REM Run MATLAB script
%MATLAB_PATH% -batch "run_skeletonize('%INPUT_FOLDER%', '%OUTPUT_FOLDER%'); exit"
