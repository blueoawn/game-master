# Production Launcher for Chat Games (PowerShell)
# Builds frontend and starts backend server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Chat Games - Production Mode" -ForegroundColor Cyan
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
Write-Host "Building frontend..." -ForegroundColor Yellow
Set-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Frontend build failed!" -ForegroundColor Red
    Set-Location ..
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ..

Write-Host ""
Write-Host "Frontend built successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "Starting backend server..." -ForegroundColor Yellow
Write-Host "Server will run on: http://localhost:5000" -ForegroundColor Green
Write-Host ""

# Start backend in a new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; python app.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow
Write-Host ""

# Open browser to Flask server
Start-Process "http://localhost:5000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Server is running!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Leaderboard scores persist in tokens.db!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close the PowerShell window to stop the server." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this launcher"
