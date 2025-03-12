@echo off
REM Check if exactly two arguments (folder path and output folder path) are provided
IF "%~2"=="" (
    echo Usage: %0 ^<input_folder^> ^<output_folder^>
    exit /b
)

REM Get the folder paths from the command-line arguments
SET INPUT_FOLDER=%~1
SET OUTPUT_FOLDER=%~2

REM Check if the MATLAB_ROOT environment variable is set
IF NOT DEFINED MATLAB_ROOT (
    REM If MATLAB_ROOT is not set, manually define the path to MATLAB here
    SET MATLAB_PATH="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\MATLAB R2022b"  REM Adjust path to your actual MATLAB installation folder
)

REM Check if the MATLAB executable exists
IF NOT EXIST "%MATLAB_PATH%" (
    echo MATLAB executable not found at %MATLAB_PATH%
    exit /b
)

REM Run the MATLAB script with the input parameters
"%MATLAB_PATH%" -batch "run_skeletonize('%INPUT_FOLDER%', '%OUTPUT_FOLDER%')"
