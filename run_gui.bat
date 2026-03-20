@echo off
echo Building React App...
cd sample-gui
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else (
    echo Venv not found at ..\venv\Scripts\activate.bat. Trying default python...
)
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    pause
    exit /b
)
echo Launching Horizon Desk GUI...
python main_gui.py
pause
