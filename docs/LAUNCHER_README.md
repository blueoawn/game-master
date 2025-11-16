# Chat Games Launcher Scripts

Easy-to-use launcher scripts for running Chat Games with a single command.

## Quick Start

### Development Mode (with hot-reload)
**Windows Batch:**
```bash
launch-dev.bat
```

**PowerShell:**
```powershell
.\launch-dev.ps1
```

This will:
- Start backend server on `http://localhost:5000`
- Start frontend dev server on `http://localhost:5173` (with hot-reload)
- Open your browser to the frontend dev server
- Keep both terminals open for debugging

### Production Mode
**Windows Batch:**
```bash
launch.bat
```

**PowerShell:**
```powershell
.\launch.ps1
```

This will:
- Build the frontend for production
- Start backend server on `http://localhost:5000`
- Open your browser to the Flask server
- Keep backend terminal open for debugging

## What Each Launcher Does

### Development Mode (`launch-dev`)
Best for active development with these features:
- **Hot-reload**: Changes to frontend code instantly appear in browser
- **Source maps**: Easy debugging with original TypeScript code
- **Fast rebuilds**: Vite rebuilds only what changed
- **Separate servers**: Frontend (5173) and backend (5000) run independently

Use this when:
- Writing new features
- Debugging frontend code
- Testing UI changes
- Active development

### Production Mode (`launch`)
Best for testing the production build:
- **Optimized build**: Minified, bundled, production-ready code
- **Single server**: Backend serves the built frontend
- **Production testing**: Test exactly what will be deployed
- **Performance**: See real production performance

Use this when:
- Testing final build
- Demonstrating to others
- Performance testing
- Pre-deployment validation

## Requirements

- **Python 3.8+** - For backend server
- **Node.js 16+** - For frontend build/dev server
- **npm** - Included with Node.js

## Troubleshooting

### "Python not found"
Install Python from [python.org](https://www.python.org/downloads/)

### "Node.js/npm not found"
Install Node.js from [nodejs.org](https://nodejs.org/)

### "Cannot run PowerShell scripts"
You may need to enable PowerShell script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port already in use
If port 5000 or 5173 is already in use:
- Check for other running instances
- Kill the process using that port
- Or modify the port in `backend/app.py` or `frontend/package.json`

### Backend errors in terminal
The backend terminal stays open so you can see errors. Common issues:
- Missing Python dependencies: Check `backend/requirements.txt`
- Database not initialized: Check Twitch bot setup
- Missing environment variables: Check `.env` file

## Advanced Usage

### Custom Ports
To change ports, edit:
- Backend: `backend/app.py` (line with `socketio.run(...)`)
- Frontend dev: `frontend/vite.config.ts` (if exists) or use `--port` flag

### Manual Commands
If you prefer running commands manually:

**Development:**
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Production:**
```bash
# Build frontend
cd frontend
npm run build

# Start backend (serves built frontend)
cd ../backend
python app.py
```

## What Gets Installed

First run will install:
- **Frontend**: Node modules (~200 MB) in `frontend/node_modules/`
- **Backend**: Python virtual environment (optional, if using venv)

These are one-time installations that get reused on subsequent runs.

## Files Created

- `launch.bat` - Production launcher (Windows batch)
- `launch-dev.bat` - Development launcher (Windows batch)
- `launch.ps1` - Production launcher (PowerShell)
- `launch-dev.ps1` - Development launcher (PowerShell)

Choose batch (.bat) or PowerShell (.ps1) based on your preference.
