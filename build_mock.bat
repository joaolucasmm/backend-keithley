@echo off
chcp 65001 > nul
echo ========================================
echo Building Keithley Controller MOCK
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
if exist "..\backend\frontend_dist_mock" rmdir /s /q "..\backend\frontend_dist_mock"
xcopy /E /I /Y "dist" "..\backend\frontend_dist_mock"

echo.
echo Step 3: Building executable for MOCK...
cd ../backend

REM Activate virtual environment
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install flask flask-cors tm-devices pywebview pyinstaller
)

REM Limpa builds anteriores
if exist "mock_build" rmdir /s /q mock_build
if exist "mock_dist" rmdir /s /q mock_dist
if exist "KeithleyController_MOCK.spec" del KeithleyController_MOCK.spec

echo.
echo Building MOCK executable with PyInstaller...
pyinstaller --onefile ^
    --name "KeithleyController_MOCK" ^
    --distpath "mock_dist" ^
    --workpath "mock_build" ^
    --specpath "." ^
    --add-data "frontend_dist_mock;frontend/dist" ^
    --add-data "mock_server.py;." ^
    --paths "venv\Lib\site-packages" ^
    --collect-all flask ^
    --collect-all flask_cors ^
    --hidden-import=jinja2 ^
    --hidden-import=werkzeug ^
    --hidden-import=click ^
    --hidden-import=itsdangerous ^
    --hidden-import=blinker ^
    --hidden-import=math ^
    --hidden-import=random ^
    --hidden-import=datetime ^
    --hidden-import=urllib ^
    --hidden-import=urllib.request ^
    --hidden-import=mock_server ^
    launcher_mock.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo Executable: mock_dist\KeithleyController_MOCK.exe
echo.

if exist "mock_dist\KeithleyController_MOCK.exe" (
    echo File size:
    dir mock_dist\KeithleyController_MOCK.exe
    echo.
    echo Testing executable...
    start "" "mock_dist\KeithleyController_MOCK.exe"
) else (
    echo ERROR: Executable not found!
    echo Check if build completed successfully.
)

echo.
pause