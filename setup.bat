@echo off
echo ================================
echo Twitch Chat Games - Setup Script
echo (Flask + Phaser 3 + TypeScript)
echo ================================
echo.

echo [1/4] Installing Python dependencies...
cd backend
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo   SUCCESS: Python dependencies installed
cd ..

echo.
echo [2/4] Installing Node.js dependencies (includes Phaser 3)...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
echo   SUCCESS: Node.js dependencies installed

echo.
echo [3/4] Building frontend (TypeScript + Vite)...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build frontend
    pause
    exit /b 1
)
echo   SUCCESS: Frontend built to dist/
cd ..

echo.
echo [4/4] Checking environment configuration...
if not exist "..\\.env" (
    echo WARNING: .env file not found in parent directory!
    echo Please create .env file with your Twitch credentials.
    echo See START_HERE.md or QUICKSTART.md for details.
) else (
    echo   SUCCESS: .env file found!
)

echo.
echo ================================
echo Setup complete! 🎮
echo ================================
echo.
echo To start the application:
echo   cd backend
echo   python app.py
echo.
echo Then:
echo   1. Open browser: http://localhost:5000
echo   2. Add to OBS as Browser Source
echo   3. Test commands in Twitch chat: !square, !circle, !boost
echo.
echo Documentation:
echo   - START_HERE.md     (Overview)
echo   - OBS_SETUP.md      (OBS Browser Source)
echo   - PHASER_GAME_TEMPLATE.md (Create new games)
echo.
pause
