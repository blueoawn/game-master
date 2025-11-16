# Quick Start Guide

> **Last Updated:** 2025-01-16
> **Estimated Time:** 10 minutes

Get your Twitch Chat Games platform running quickly! This guide covers installation, configuration, and verification.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Development Mode](#development-mode)
- [Testing Commands](#testing-commands)
- [Admin Panel Access](#admin-panel-access)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Download |
|----------|----------------|----------|
| **Python** | 3.11+ | [python.org](https://python.org) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org) |
| **Git** | Latest | [git-scm.com](https://git-scm.com) |

### Twitch Requirements

- ✅ Twitch Developer Application ([Create one here](https://dev.twitch.tv/console/apps))
- ✅ OAuth tokens configured
- ✅ Bot account (recommended, not required)

---

## Installation Steps

### 1. Install Python Dependencies

```bash
cd chat-games/backend
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed Flask-2.3.0 Flask-SocketIO-5.3.0 python-socketio-5.9.0 ...
```

### 2. Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

**Expected output:**
```
added 347 packages in 15s
```

### 3. Build Frontend for Production

```bash
npm run build
```

**Expected output:**
```
✓ built in 3.2s
dist/index.html                   1.2 kB
dist/assets/index-abc123.js       245 kB
```

---

## Configuration

### Environment Variables

Create or edit `.env` file in **project root** (`stream tools/.env`):

```bash
# Twitch Application Credentials
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here

# Twitch User IDs (numeric)
BOT_ID=123456789          # Bot account user ID
OWNER_ID=987654321        # Your user ID (for mod commands)
```

### How to Get These Values

<details>
<summary><strong>Finding Your Client ID & Secret</strong></summary>

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Create a new application or select existing
3. Copy **Client ID**
4. Click "New Secret" to generate **Client Secret**
5. Set OAuth Redirect URL to `http://localhost:3000`
</details>

<details>
<summary><strong>Finding Your User IDs</strong></summary>

Use [Twitch User ID Lookup](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/)

- Enter bot username → Get BOT_ID
- Enter your username → Get OWNER_ID
</details>

---

## Running the Application

### Standard Mode (Production)

```bash
cd backend
python app.py
```

**Success indicators:**
```
INFO:werkzeug: * Running on http://0.0.0.0:5000
INFO:GameManager: GameManager initialized
INFO:GameManager: Found 1 games
INFO:GameManager: Loaded initial game: chat_minigames
```

**Access the app:** Open browser to `http://localhost:5000`

<!--
🎥 **Video Tutorial** (Placeholder)
Add screencast of first-time setup here
-->

---

## Development Mode

For **hot-reload** during development, run backend and frontend separately:

### Terminal 1: Backend Server

```bash
cd backend
python app.py
```

Leave running. Flask will auto-reload on Python file changes.

### Terminal 2: Frontend Dev Server

```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v4.5.0  ready in 245 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Access dev server:** `http://localhost:3000`

**Benefits:**
- ⚡ Instant HMR (Hot Module Replacement)
- 🔍 Better error messages
- 🎨 Source maps for debugging

### Port Reference

| Port | Service | URL | Use Case |
|------|---------|-----|----------|
| **5000** | Flask Backend | `http://localhost:5000` | Production, Admin Panel |
| **3000** | Vite Dev Server | `http://localhost:3000` | Frontend Development |

---

## Testing Commands

Once running, test the platform with these chat commands:

### Basic Commands (Any Viewer)

| Command | Effect | Expected Result |
|---------|--------|----------------|
| `!square` | Spawn square shape | Shape appears with your username |
| `!circle` | Spawn circle shape | Colored circle falls from top |
| `!triangle` | Spawn triangle shape | Triangle spawns with physics |
| `!boost` | Launch all shapes up | All shapes rocket upward |
| `!explode` | Explode from center | Shapes fly outward |

### Moderator Commands

| Command | Effect | Permission |
|---------|--------|-----------|
| `!clear` | Clear all shapes | Moderator/Broadcaster |
| `!nextgame` | Switch to next game | Moderator/Broadcaster |

### Testing Without Twitch

Use browser console to simulate commands:

```javascript
// Open browser console (F12) and run:
socket.emit('game_state_update', {
    shape_added: {
        id: 'test_1',
        type: 'square',
        x: 500,
        y: 200,
        color: '#FF6B6B',
        username: 'TestUser'
    }
});
```

---

## Admin Panel Access

Manage leaderboards and player scores via the admin panel:

**URL:** `http://localhost:5000/admin`

### Admin Features

- View live leaderboard with statistics
- Reset individual player scores
- Set custom scores manually
- Clear all scores (with confirmation)

**Health Check Endpoint:** `http://localhost:5000/api/admin/health`

---

## Troubleshooting

### Common Issues

<details>
<summary><strong>❌ "Module not found" errors</strong></summary>

**Cause:** Missing dependencies

**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```
</details>

<details>
<summary><strong>❌ Frontend shows blank page / 404</strong></summary>

**Cause:** Frontend not built

**Solution:**
```bash
cd frontend
npm run build
```

**Verify:** Check `frontend/dist/` exists and contains `index.html`
</details>

<details>
<summary><strong>❌ Twitch bot not connecting</strong></summary>

**Possible Causes:**

1. **Invalid .env file**
   - Check `.env` is in **project root** (not `backend/`)
   - Verify all 4 variables are set

2. **Expired OAuth tokens**
   - Regenerate Client Secret in Twitch Developer Console

3. **Wrong user IDs**
   - IDs must be numeric, not usernames
   - Use ID lookup tool to verify

**Check Connection:**
Look for this in Flask console:
```
INFO:TwitchBot: Bot connected to Twitch
```
</details>

<details>
<summary><strong>❌ SocketIO connection failed</strong></summary>

**Symptoms:**
- Browser console shows connection errors
- No real-time updates

**Solutions:**

1. **Verify Flask is running:**
   ```bash
   curl http://localhost:5000/api/admin/health
   ```

2. **Check firewall:**
   - Allow port 5000
   - Disable firewall temporarily to test

3. **Browser console check:**
   - Open DevTools (F12)
   - Look for WebSocket connection errors
   - Should see: `✅ Connected to server`
</details>

<details>
<summary><strong>❌ Commands not working in chat</strong></summary>

**Checklist:**

- [ ] Bot is connected (check Flask console)
- [ ] Using correct prefix (`!` by default)
- [ ] Command is valid (see [Testing Commands](#testing-commands))
- [ ] No cooldowns active
- [ ] User has required permissions (for mod commands)

**Debug Mode:**
Enable debug logging in `backend/app.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```
</details>

<details>
<summary><strong>❌ Leaderboard not updating</strong></summary>

**Possible Causes:**

1. **Database not created**
   - First time running? Twitch bot creates table on startup
   - Check: `backend/tokens.db` exists

2. **Table doesn't exist**
   - Visit: `http://localhost:5000/api/admin/health`
   - Should show: `"table_exists": true`

3. **Score events not firing**
   - Check Flask console for database errors
   - Verify shapes are hitting targets
</details>

### Getting Help

If issues persist:

1. **Check Flask console** for error messages
2. **Check browser console** (F12) for frontend errors
3. **Review logs** in `backend/` directory
4. **Open an issue** on GitHub with logs attached

---

## Next Steps

### Recommended Path

1. ✅ **Get familiar with commands** - Test all available commands
2. ✅ **Try the admin panel** - Manage leaderboards
3. 📖 **Read full documentation** - [README.md](../README.md)
4. 🎨 **Configure OBS** - [OBS Setup Guide](OBS_SETUP.md)
5. 🎮 **Create your own game** - [Phaser Game Template](PHASER_GAME_TEMPLATE.md)

### Learning Resources

| Resource | Topic |
|----------|-------|
| [State Management Guide](../STATE_MANAGEMENT.md) | Understanding data flow |
| [File Locations](FILE_LOCATIONS.md) | Project structure reference |
| [Phaser 3 Docs](https://photonstorm.github.io/phaser3-docs/) | Game engine documentation |
| [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/) | Real-time communication |

---

## Reference: Key File Paths

Quick reference for important files:

| Purpose | Path | Description |
|---------|------|-------------|
| **Frontend Entry** | `frontend/src/main.ts` | TypeScript entry point |
| **Frontend Build** | `frontend/dist/` | Built files (Flask serves this) |
| **Backend Entry** | `backend/app.py` | Flask application |
| **Game Discovery** | `backend/games/` | Auto-discovered games |
| **Admin Panel** | `backend/templates/admin.html` | Web-based admin UI |
| **Database** | `backend/tokens.db` | SQLite database (auto-created) |
| **Environment Config** | `../../.env` | Twitch OAuth credentials |

---

## Verification Checklist

Use this checklist to verify successful setup:

- [ ] **Backend running** - Flask console shows "Running on http://0.0.0.0:5000"
- [ ] **Frontend built** - `frontend/dist/index.html` exists
- [ ] **Browser loads** - `http://localhost:5000` shows game
- [ ] **Game discovered** - Flask console shows "Found 1 games"
- [ ] **Twitch bot connected** - Console shows "Bot connected to Twitch"
- [ ] **SocketIO connected** - Browser console shows "Connected to server"
- [ ] **Commands work** - `!square` spawns a shape
- [ ] **Leaderboard updates** - Scores appear after hitting targets
- [ ] **Admin panel accessible** - `http://localhost:5000/admin` loads

---

> **Ready to stream?** Configure OBS Browser Source - see [OBS_SETUP.md](OBS_SETUP.md)

---

**Happy streaming!** 🎮🎉
