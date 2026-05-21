@echo off
echo ========================================
echo Final Build - Keithley Controller
echo ========================================
echo.

echo Step 1: Building Vue frontend...
cd ../frontend
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
)
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Vue build failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Copying frontend to backend...
xcopy /E /I /Y "dist" "../backend/frontend_dist"

echo.
echo Step 3: Building executable...
cd ../backend

REM Activate virtual environment
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
) else (
    python -m venv venv
    call venv\Scripts\activate
    pip install flask flask-cors tm-devices pywebview pyinstaller
)

echo.
echo Building with PyInstaller...
pyinstaller --onefile ^
    --name "KeithleyController" ^
    --add-data "frontend_dist;frontend/dist" ^
    --paths "venv\Lib\site-packages" ^
    --collect-all flask ^
    --collect-all flask_cors ^
    --collect-all tm_devices ^
    --hidden-import=jinja2 ^
    --hidden-import=werkzeug ^
    --hidden-import=click ^
    --hidden-import=itsdangerous ^
    --hidden-import=blinker ^
    launcher_simple.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo Executable: dist\KeithleyController.exe
echo.

if exist "dist\KeithleyController.exe" (
    echo Testing executable...
    dist\KeithleyController.exe
) else (
    echo ERROR: Executable not found!
)

pause