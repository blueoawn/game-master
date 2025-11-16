@echo off
echo ================================
echo Twitch Chat Games - Verification
echo ================================
echo.

set ERROR_COUNT=0

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   ERROR: Python not found!
    set /a ERROR_COUNT+=1
) else (
    python --version
)

echo.
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   ERROR: Node.js not found!
    set /a ERROR_COUNT+=1
) else (
    node --version
)

echo.
echo [3/6] Checking backend dependencies...
if not exist "backend\game_loader.py" (
    echo   ERROR: Backend files not found!
    set /a ERROR_COUNT+=1
) else (
    echo   OK: Backend files found
)

echo.
echo [4/6] Checking frontend source...
if not exist "frontend\src\main.ts" (
    echo   ERROR: Frontend source not found!
    set /a ERROR_COUNT+=1
) else (
    echo   OK: Frontend source found
)

echo.
echo [5/6] Checking frontend build...
if not exist "frontend\dist\index.html" (
    echo   WARNING: Frontend not built yet!
    echo   Run: cd frontend ^&^& npm run build
    set /a ERROR_COUNT+=1
) else (
    echo   OK: Frontend built
)

echo.
echo [6/6] Checking environment configuration...
if not exist "..\\.env" (
    echo   WARNING: .env file not found in parent directory!
    echo   You'll need this for Twitch bot integration.
) else (
    echo   OK: .env file found
)

echo.
echo ================================
if %ERROR_COUNT% EQU 0 (
    echo Status: READY TO RUN
    echo.
    echo To start:
    echo   cd backend
    echo   python app.py
    echo.
    echo Then open: http://localhost:5000
) else (
    echo Status: SETUP INCOMPLETE
    echo Found %ERROR_COUNT% issue(s^)
    echo.
    echo Run setup.bat to install dependencies
)
echo ================================
echo.
pause
