@echo off
REM Development Launcher for Chat Games
REM Starts backend + frontend dev server with hot-reload

echo ========================================
echo   Chat Games - Development Mode
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

REM Install backend dependencies if needed
echo Checking backend dependencies...
if not exist "backend\.venv" (
    echo Creating virtual environment...
    python -m venv backend\.venv
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
echo Starting backend server...
echo Backend will run on: http://localhost:5000
echo.

REM Start backend in a new terminal
start "Chat Games - Backend" cmd /k "cd /d "%~dp0backend" && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo.
echo Starting frontend dev server...
echo Frontend will run on: http://localhost:5173
echo.

REM Start frontend dev server in a new terminal
start "Chat Games - Frontend Dev" cmd /k "cd /d "%~dp0frontend" && npm run dev"

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo Opening browser...
echo.

REM Open browser to frontend dev server (with hot-reload)
start http://localhost:5173

echo.
echo ========================================
echo   Both servers are running!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173 (with hot-reload)
echo.
echo Leaderboard scores persist in tokens.db!
echo.
echo Close the terminal windows to stop the servers.
echo.
pause
