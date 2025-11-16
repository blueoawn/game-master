# Development Launcher for Chat Games (PowerShell)
# Starts backend + frontend dev server with hot-reload

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Chat Games - Development Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found! Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node is available
try {
    $nodeVersion = node --version 2>&1
    $npmVersion = npm --version 2>&1
    Write-Host "Found: Node $nodeVersion, npm $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js/npm not found! Please install Node.js" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install frontend dependencies if needed
Write-Host ""
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Yellow
Write-Host "Backend will run on: http://localhost:5000" -ForegroundColor Green
Write-Host ""

# Start backend in a new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; python app.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting frontend dev server..." -ForegroundColor Yellow
Write-Host "Frontend will run on: http://localhost:5173" -ForegroundColor Green
Write-Host ""

# Start frontend dev server in a new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; npm run dev" -WindowStyle Normal

# Wait for frontend to start
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow
Write-Host ""

# Open browser to frontend dev server
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Both servers are running!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173 (with hot-reload)" -ForegroundColor Green
Write-Host ""
Write-Host "Leaderboard scores persist in tokens.db!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close the PowerShell windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this launcher"
