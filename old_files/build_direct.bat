@echo off
echo ========================================
echo Building Keithley Controller - Direct Method
echo ========================================
echo.

echo 1. Building Vue frontend...
cd ../frontend
call npm run build
if %errorlevel% neq 0 (
    echo Error building frontend!
    pause
    exit /b %errorlevel%
)

echo.
echo 2. Building executable...
cd ../backend

REM Desativa ambiente virtual se existir
call deactivate 2>nul

REM Instala pyinstaller se não tiver
pip show pyinstaller > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pyinstaller...
    pip install pyinstaller
)

REM Executa pyinstaller com coleta de todas dependências
pyinstaller --onefile ^
    --name "KeithleyController" ^
    --add-data "../frontend/dist;frontend/dist" ^
    --collect-all flask ^
    --collect-all flask_cors ^
    --collect-all tm_devices ^
    --collect-all webview ^
    --hidden-import=jinja2 ^
    --hidden-import=markupsafe ^
    --hidden-import=werkzeug ^
    --hidden-import=click ^
    --hidden-import=itsdangerous ^
    --hidden-import=blinker ^
    --hidden-import=websocket ^
    --hidden-import=usb ^
    --hidden-import=libusb_package ^
    --paths "%CD%\venv\Lib\site-packages" ^
    launcher.py

echo.
echo ========================================
echo Build complete!
echo Executable: dist\KeithleyController.exe
echo Size: 
dir dist\KeithleyController.exe
echo ========================================
pause