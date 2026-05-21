@echo off
echo ========================================
echo Building Keithley Controller Desktop App
echo ========================================
echo.

REM Ativar ambiente virtual (se existir)
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
)

echo 1. Verificando dependencias...
pip show flask > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask...
    pip install flask flask-cors
)

pip show tm-devices > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing tm-devices...
    pip install tm-devices
)

pip show pywebview > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pywebview...
    pip install pywebview
)

echo.
echo 2. Building Vue frontend...
cd ../frontend
if exist "node_modules" (
    call npm run build
) else (
    echo Installing npm dependencies first...
    call npm install
    call npm run build
)
if %errorlevel% neq 0 (
    echo Error building frontend!
    pause
    exit /b %errorlevel%
)

echo.
echo 3. Building executable with PyInstaller...
cd ../backend
pyinstaller keithley.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo Error building executable!
    echo.
    echo Trying alternative method...
    pyinstaller --onefile --add-data "../frontend/dist;frontend/dist" --hidden-import=flask --hidden-import=flask_cors --hidden-import=tm_devices --hidden-import=webview launcher.py
)

echo.
echo ========================================
echo Build complete!
echo Executable located at: dist/KeithleyController.exe
echo ========================================
echo.
echo To test the executable, run:
echo dist\KeithleyController.exe
echo.
pause