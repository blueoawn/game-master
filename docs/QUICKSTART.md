# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- Twitch Developer Application configured

## Installation

### 1. Install Backend Dependencies
```bash
cd chat-games/backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd chat-games/frontend
npm install
```

### 3. Configure Environment
Make sure `.env` exists in `stream-tools/` root:
```
CLIENT_ID=your_twitch_client_id
CLIENT_SECRET=your_twitch_client_secret
BOT_ID=your_bot_user_id
OWNER_ID=your_user_id
```

### 4. Build Frontend
```bash
cd chat-games/frontend
npm run build
```

### 5. Run!
```bash
cd chat-games/backend
python app.py
```

Open browser to: **http://localhost:5000**

## Development Mode

**Terminal 1 (Backend):**
```bash
cd chat-games/backend
python app.py
```

**Terminal 2 (Frontend with hot-reload):**
```bash
cd chat-games/frontend
npm run dev
```

Open: **http://localhost:3000**

## Testing

Try these commands in your Twitch chat:
- `!square` - Spawn a square
- `!circle` - Spawn a circle
- `!boost` - Boost all shapes
- `!explode` - Explode shapes
- `!nextgame` - Switch games (mod only)

## File Paths to Know

| What | Where |
|------|-------|
| **Frontend Entry** | `frontend/public/index.html` |
| **Frontend Build Output** | `frontend/dist/` |
| **Flask Serves From** | `frontend/dist/index.html` |
| **Backend Entry** | `backend/app.py` |
| **Game Discovery** | `games/builtin/` and `submodules/` |

**Important**: Flask serves the built frontend from `frontend/dist/`. In development mode, Vite dev server runs on port 3000 and proxies API calls to Flask on port 5000.

## Verification

Run verification script to check everything:
```bash
verify.bat
```

## Troubleshooting

**"Module not found" errors?**
- Make sure you installed dependencies in both `backend/` and `frontend/`

**Frontend shows 404?**
- Run `npm run build` in `frontend/` directory
- Flask serves from `frontend/dist/index.html`

**Twitch bot not connecting?**
- Check your `.env` file has all required fields in `stream-tools/.env`
- Verify tokens are valid

**SocketIO connection failed?**
- Make sure Flask is running on port 5000
- Check firewall isn't blocking the port
- Look for errors in browser console (F12)

## Next Steps

- Read [README_NEW.md](README_NEW.md) for full documentation
- Learn how to create custom games
- Add community games as submodules

Happy streaming! 🎮
