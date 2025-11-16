@echo off
REM Production Launcher for Chat Games
REM Builds frontend and starts backend server

echo ========================================
echo   Chat Games - Production Mode
echo ========================================
echo.

REM Change to chat-games directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node is available
call npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js/npm not found! Please install Node.js
    pause
    exit /b 1
)

REM Install frontend dependencies if needed
echo Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo Building frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo Frontend built successfully!
echo.

echo Starting backend server...
echo Server will run on: http://localhost:5000
echo.

REM Start backend in a new terminal
start "Chat Games - Backend" cmd /k "cd /d "%~dp0backend" && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo.
echo Opening browser...
echo.

REM Open browser to Flask server (serves built frontend)
start http://localhost:5000

echo.
echo ========================================
echo   Server is running!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo.
echo Leaderboard scores persist in tokens.db!
echo.
echo Close the backend terminal to stop the server.
echo.
pause
