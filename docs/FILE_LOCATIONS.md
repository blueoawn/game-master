# File Locations Reference

> **Purpose:** Quick lookup for project file paths and structure

Complete reference guide for navigating the Twitch Chat Games platform codebase. Use this document to quickly find files, understand directory organization, and locate specific functionality.

---

## Table of Contents

- [Quick Reference Table](#quick-reference-table)
- [Directory Structure](#directory-structure)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [Game Module Structure](#game-module-structure)
- [Configuration Files](#configuration-files)
- [Development Commands](#development-commands)
- [Common Paths by Task](#common-paths-by-task)

---

## Quick Reference Table

### Core Application Files

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **Flask Entry Point** | [backend/app.py](../backend/app.py) | Main server, SocketIO, routing |
| **Frontend Entry Point** | [frontend/src/main.ts](../frontend/src/main.ts) | TypeScript initialization |
| **HTML Entry Point** | [frontend/public/index.html](../frontend/public/index.html) | Root HTML document |
| **Game Registry** | [frontend/src/games/registry.ts](../frontend/src/games/registry.ts) | Game component registration |
| **Twitch Bot** | [backend/twitch_bot.py](../backend/twitch_bot.py) | Twitch chat integration |
| **Admin Panel** | [backend/templates/admin.html](../backend/templates/admin.html) | Leaderboard management UI |
| **Database** | `backend/tokens.db` | SQLite database (auto-created) |

### System Architecture Files

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **Base Game Class** | [backend/base_game.py](../backend/base_game.py) | Abstract base for all games |
| **Game Loader** | [backend/game_loader.py](../backend/game_loader.py) | Auto-discovery system |
| **Game Manager** | [backend/game_manager.py](../backend/game_manager.py) | Game lifecycle management |
| **Socket Client** | [frontend/src/socket.ts](../frontend/src/socket.ts) | SocketIO client initialization |
| **Game Manager (Frontend)** | [frontend/src/gameManager.ts](../frontend/src/gameManager.ts) | Frontend game coordinator |
| **Type Definitions** | [frontend/src/types.ts](../frontend/src/types.ts) | TypeScript interfaces |

### Game Modules

| Game | Backend | Frontend |
|------|---------|----------|
| **Chat Minigames** | [backend/games/chat_minigames/](../backend/games/chat_minigames/) | [frontend/src/games/ChatMinigames.ts](../frontend/src/games/ChatMinigames.ts) |
| **Shape Smash Minigame** | [backend/games/chat_minigames/minigames/shape_smash.py](../backend/games/chat_minigames/minigames/shape_smash.py) | [frontend/src/games/chat-minigames/ShapeSmashScene.ts](../frontend/src/games/chat-minigames/ShapeSmashScene.ts) |

---

## Directory Structure

### Complete Project Tree

```
stream tools/
├── .env                          ← Twitch OAuth credentials (YOU create this)
│
└── chat-games/
    ├── README.md                 ← Project overview
    ├── STATE_MANAGEMENT.md       ← State flow documentation
    │
    ├── backend/                  ← Python Flask server
    │   ├── app.py               ← 🚀 Main entry point
    │   ├── base_game.py         ← Abstract game base class
    │   ├── game_loader.py       ← Game discovery system
    │   ├── game_manager.py      ← Game lifecycle coordinator
    │   ├── twitch_bot.py        ← Twitch chat integration
    │   ├── requirements.txt     ← Python dependencies
    │   ├── tokens.db            ← SQLite database (auto-created)
    │   │
    │   ├── templates/           ← Server-rendered HTML
    │   │   └── admin.html       ← Admin panel UI
    │   │
    │   └── games/               ← 🎮 Game modules directory
    │       └── chat_minigames/
    │           ├── game_manifest.json
    │           ├── backend/
    │           │   └── game.py
    │           └── minigames/
    │               └── shape_smash.py
    │
    ├── frontend/                ← TypeScript Vite application
    │   ├── public/
    │   │   └── index.html       ← HTML entry point
    │   │
    │   ├── src/
    │   │   ├── main.ts          ← 🚀 TypeScript entry point
    │   │   ├── socket.ts        ← SocketIO client
    │   │   ├── gameManager.ts   ← Frontend game coordinator
    │   │   ├── types.ts         ← TypeScript interfaces
    │   │   │
    │   │   └── games/           ← Frontend game components
    │   │       ├── registry.ts  ← Game registration
    │   │       ├── PhaserGameBase.ts
    │   │       ├── ChatMinigames.ts
    │   │       └── chat-minigames/
    │   │           └── ShapeSmashScene.ts
    │   │
    │   ├── dist/                ← [GENERATED] Built files
    │   │   ├── index.html
    │   │   └── assets/
    │   │       └── index-[hash].js
    │   │
    │   ├── package.json         ← Node dependencies
    │   ├── tsconfig.json        ← TypeScript config
    │   └── vite.config.ts       ← Vite build config
    │
    ├── submodules/              ← Git submodules for external games
    │
    ├── docs/                    ← Documentation
    │   ├── QUICKSTART.md        ← Installation guide
    │   ├── PHASER_GAME_TEMPLATE.md
    │   ├── FILE_LOCATIONS.md    ← This file
    │   └── OBS_SETUP.md         ← Streaming setup
    │
    └── tools/                   ← Development utilities
```

<!--
📊 **Interactive Structure Explorer** (Placeholder)
Add interactive directory visualization or expandable tree diagram here
-->

---

## Frontend Architecture

### Development vs Production

| Environment | Port | URL | Files Served | Use Case |
|-------------|------|-----|--------------|----------|
| **Development** | 3000/5173 | `http://localhost:3000` | Live source files | Hot-reload development |
| **Production** | 5000 | `http://localhost:5000` | `frontend/dist/` | Testing/deployment |

### Frontend File Purposes

| File | Purpose | When to Edit |
|------|---------|--------------|
| `public/index.html` | Root HTML document | Rarely (add global meta tags) |
| `src/main.ts` | App initialization, SocketIO setup | Adding global features |
| `src/socket.ts` | SocketIO client configuration | Changing WebSocket settings |
| `src/gameManager.ts` | Game loading and state routing | Modifying game lifecycle |
| `src/types.ts` | TypeScript interfaces | Adding new data structures |
| `src/games/registry.ts` | **Game registration** | **Adding new games** |
| `src/games/PhaserGameBase.ts` | Base class for Phaser games | Creating Phaser utilities |

### Build Output (`frontend/dist/`)

**Generated by:** `npm run build`

```
dist/
├── index.html           ← HTML with injected script tags
└── assets/
    ├── index-[hash].js  ← Bundled JavaScript (TypeScript compiled)
    └── index-[hash].css ← Bundled CSS (if any)
```

**Flask serves this directory in production** via catch-all route.

---

## Backend Architecture

### Backend File Purposes

| File | Purpose | When to Edit |
|------|---------|--------------|
| `app.py` | Flask server, SocketIO, routes | Adding API endpoints, middleware |
| `base_game.py` | Abstract base class for games | Rarely (core game interface) |
| `game_loader.py` | Discovers games via manifests | Adding search paths |
| `game_manager.py` | Game lifecycle management | Changing game switching logic |
| `twitch_bot.py` | Twitch chat connection, OAuth | Modifying chat behavior |
| `templates/admin.html` | Admin panel UI | Customizing admin interface |

### Database Structure

**Location:** `backend/tokens.db` (auto-created on first run)

**Tables:**
- `player_scores` - Username, score, timestamp

**Access:**
- **Admin Panel:** `http://localhost:5000/admin`
- **Health Check API:** `http://localhost:5000/api/admin/health`

---

## Game Module Structure

### Standard Game Layout

Every game module follows this structure:

```
backend/games/my_game/
├── game_manifest.json          ← Required: Game metadata
├── backend/
│   └── game.py                ← Required: Python game class
├── minigames/                 ← Optional: For game collections
│   └── sub_game.py
└── assets/                    ← Optional: Game-specific assets
```

### Chat Minigames Example

**Full structure:**
```
backend/games/chat_minigames/
├── game_manifest.json
│   {
│     "id": "chat_minigames",
│     "backend": {"entry_point": "game:ChatMinigamesGame"},
│     "frontend": {"component": "ChatMinigames"}
│   }
│
├── backend/
│   └── game.py               ← ChatMinigamesGame class
│
└── minigames/
    └── shape_smash.py        ← ShapeSmashMinigame class
```

**Frontend component:**
```
frontend/src/games/
├── ChatMinigames.ts          ← Main game container
└── chat-minigames/
    └── ShapeSmashScene.ts    ← Phaser scene
```

**Registry entry:**
```typescript
// frontend/src/games/registry.ts
import { ChatMinigames } from './ChatMinigames';

private static games = new Map([
  ['ChatMinigames', ChatMinigames],
]);
```

### Game Discovery Paths

Games are auto-discovered from:

| Path | Purpose | Priority |
|------|---------|----------|
| `backend/games/` | Built-in games | 1 (searched first) |
| `submodules/` | External Git submodules | 2 (searched second) |

**Requirements for discovery:**
- ✅ Valid `game_manifest.json` at game root
- ✅ Python class at `backend.entry_point` path
- ✅ Frontend component registered in `registry.ts`

---

## Configuration Files

### Environment Variables (`.env`)

**Location:** `stream tools/.env` (project root, **NOT** `chat-games/.env`)

```bash
# Required for Twitch bot
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
BOT_ID=bot_user_id
OWNER_ID=your_user_id
```

📖 **See [QUICKSTART.md](QUICKSTART.md#configuration) for obtaining these values**

### Package Configuration

| File | Purpose | Key Settings |
|------|---------|--------------|
| `frontend/package.json` | Node dependencies, scripts | `scripts`: dev, build, type-check |
| `backend/requirements.txt` | Python dependencies | Flask, Flask-SocketIO, TwitchIO |
| `frontend/tsconfig.json` | TypeScript compiler | `target`: ES2020, `strict`: true |
| `frontend/vite.config.ts` | Vite build settings | Dev server proxy, build output |

---

## Development Commands

### Quick Command Reference

| Task | Command | Working Directory |
|------|---------|-------------------|
| **Start Backend** | `python app.py` | `backend/` |
| **Start Frontend Dev Server** | `npm run dev` | `frontend/` |
| **Build Frontend** | `npm run build` | `frontend/` |
| **Type Check (no build)** | `npm run type-check` | `frontend/` |
| **Install Python Dependencies** | `pip install -r requirements.txt` | `backend/` |
| **Install Node Dependencies** | `npm install` | `frontend/` |

### Workflow Paths

**Production Deployment:**
```bash
# From project root (stream tools/chat-games/)
cd backend && pip install -r requirements.txt
cd ../frontend && npm install && npm run build
cd ../backend && python app.py

# Access: http://localhost:5000
```

**Development Mode (Hot-Reload):**
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && npm run dev

# Access: http://localhost:3000 (proxies to backend:5000)
```

---

## Common Paths by Task

### Adding a New Game

| Step | File/Directory | Action |
|------|---------------|--------|
| 1. Create structure | `backend/games/my_game/` | `mkdir -p backend/games/my_game/backend` |
| 2. Write manifest | `backend/games/my_game/game_manifest.json` | Create JSON with id, entry_point, component |
| 3. Create backend | `backend/games/my_game/backend/game.py` | Extend `BaseGame` class |
| 4. Create frontend | `frontend/src/games/MyGame.ts` | Create Phaser game component |
| 5. Register | `frontend/src/games/registry.ts` | Add `['MyGame', MyGame]` to Map |
| 6. Build & test | `frontend/` | `npm run build` then start backend |

📖 **See [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md) for complete guide**

### Modifying Existing Game

| What to Change | Backend | Frontend |
|---------------|---------|----------|
| **Add command** | `backend/games/.../backend/game.py` → `get_commands()` | Handle in scene's `onStateUpdate()` |
| **Add visual element** | N/A | `frontend/src/games/.../Scene.ts` → `create()` |
| **Change game logic** | `backend/games/.../backend/game.py` | N/A |
| **Modify rendering** | N/A | `frontend/src/games/.../Scene.ts` → `onStateUpdate()` |
| **Update state** | Emit via `emit_state()` or `emit_event()` | Receive in `onStateUpdate()` |

### Debugging

| Issue | Check File | What to Look For |
|-------|------------|------------------|
| **Game not discovered** | `backend/games/my_game/game_manifest.json` | Valid JSON, correct `entry_point` |
| **Frontend not loading** | `frontend/dist/index.html` | File exists (run `npm run build`) |
| **SocketIO errors** | Browser console (F12) | Connection status, errors |
| **Command not working** | `backend/app.py` console | Flask logs, command registration |
| **Import errors** | `backend/games/.../backend/game.py` | Path calculation (`'../..'` for games) |
| **Type errors** | Terminal | `npm run type-check` output |

### Accessing Admin Features

| Feature | URL | Authentication |
|---------|-----|----------------|
| **Admin Panel** | `http://localhost:5000/admin` | None (localhost only) |
| **Health Check** | `http://localhost:5000/api/admin/health` | None |
| **Leaderboard API** | Via SocketIO `get_leaderboard_admin` event | None |

---

## Port Reference

| Port | Service | URL | Purpose |
|------|---------|-----|---------|
| **5000** | Flask Backend | `http://localhost:5000` | Production serving, admin panel, API |
| **3000** | Vite Dev Server | `http://localhost:3000` | Frontend development with HMR |
| **5173** | Vite (alternate) | `http://localhost:5173` | If port 3000 is in use |

**Note:** In development mode, Vite proxies API requests to Flask backend (port 5000).

---

## Resources

### Related Documentation

- 📖 [README.md](../README.md) - Project overview and architecture
- 📖 [QUICKSTART.md](QUICKSTART.md) - Installation and setup
- 📖 [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md) - Creating new games
- 📖 [STATE_MANAGEMENT.md](../STATE_MANAGEMENT.md) - State flow patterns
- 📖 [OBS_SETUP.md](OBS_SETUP.md) - Streaming configuration

### External References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vite Documentation](https://vitejs.dev/)
- [Phaser 3 API](https://photonstorm.github.io/phaser3-docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Need to find a specific file?** Use your IDE's file search (`Ctrl+P` / `Cmd+P`) with these patterns:
- `**/game.py` - Find all backend game files
- `**/*Scene.ts` - Find all Phaser scenes
- `**/game_manifest.json` - Find all game manifests
- `**/registry.ts` - Find frontend game registry

> **Tip:** Bookmark this document for quick reference during development!
