# Twitch Chat Games Platform

> **Version:** 2.0
> **Last Updated:** 2025-01-16
> **Architecture:** Flask (Python) + Vite (TypeScript) + Phaser 3

A modular, real-time interactive gaming platform where your Twitch chat controls the action! Built with modern web technologies for smooth performance and easy extensibility.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Available Games](#available-games)
- [Admin Panel](#admin-panel)
- [Development](#development)
- [Adding New Games](#adding-new-games)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Overview

Twitch Chat Games is a real-time multiplayer platform that bridges Twitch chat and browser-based games. Viewers send commands via chat, and the game responds instantly with visual feedback.

### Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Flask + Flask-SocketIO | Real-time WebSocket server |
| **Frontend** | Vite + TypeScript | Fast development & type safety |
| **Game Engine** | Phaser 3 | Physics & rendering |
| **Chat Integration** | TwitchIO | Twitch bot framework |
| **Database** | SQLite | Persistent leaderboards |

<!--
📹 **Video Overview** (Placeholder)
Add a video demo of the platform in action here
-->

---

## Features

✅ **Real-Time Communication** - WebSocket-based instant state synchronization
✅ **Modular Architecture** - Easily add/remove games via submodules
✅ **Leaderboard System** - Persistent scoring with SQLite database
✅ **Admin Panel** - Web-based score management at `/admin`
✅ **Hot-Reload Development** - Fast iteration with Vite dev server
✅ **Type Safety** - Full TypeScript support prevents runtime errors
✅ **Auto-Discovery** - Games self-register via JSON manifests
✅ **Phaser 3 Engine** - Professional-grade 2D physics and rendering

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Twitch Developer Application (for OAuth tokens)

### Installation

```bash
# 1. Clone repository
cd "stream tools/chat-games"

# 2. Install Python dependencies
cd backend
pip install -r requirements.txt

# 3. Install frontend dependencies
cd ../frontend
npm install

# 4. Build frontend
npm run build

# 5. Configure environment variables
# Create .env in project root with:
CLIENT_ID=your_twitch_client_id
CLIENT_SECRET=your_twitch_client_secret
BOT_ID=your_bot_user_id
OWNER_ID=your_user_id

# 6. Start server
cd ../backend
python app.py
```

**Access the application:** `http://localhost:5000`

📖 **See [docs/QUICKSTART.md](docs/QUICKSTART.md) for detailed setup instructions.**

---

## Architecture

### System Overview

```
┌─────────────────┐
│  Twitch Chat    │
│  (!square)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  TwitchIO Bot   │─────▶│  Game Backend    │
│  (Python)       │      │  (BaseGame)      │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  │ emit_state()
                                  ▼
                         ┌─────────────────┐
                         │ Flask-SocketIO  │
                         │  (WebSocket)    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Frontend Game   │
                         │ (Phaser Scene)  │
                         └─────────────────┘
```

<!--
📊 **Architecture Diagram** (Placeholder)
Add detailed architecture diagram showing all components here
-->

### Directory Structure

```
chat-games/
├── backend/                    # Python Flask application
│   ├── app.py                 # Flask entry point + SocketIO server
│   ├── base_game.py           # Abstract base class for all games
│   ├── game_loader.py         # Auto-discovery system
│   ├── game_manager.py        # Game lifecycle management
│   ├── twitch_bot.py          # Twitch chat integration
│   ├── templates/             # Server-rendered pages
│   │   └── admin.html         # Admin panel UI
│   └── games/                 # ⭐ Game modules directory
│       └── chat_minigames/    # Example: Chat Minigames collection
│           ├── game_manifest.json
│           ├── backend/
│           │   └── game.py    # Python game orchestrator
│           └── minigames/
│               └── shape_smash.py
│
├── frontend/                   # TypeScript Vite application
│   ├── src/
│   │   ├── main.ts            # Entry point
│   │   ├── socket.ts          # SocketIO client
│   │   ├── gameManager.ts     # Frontend game coordinator
│   │   ├── types.ts           # TypeScript interfaces
│   │   └── games/
│   │       ├── registry.ts    # Game component registry
│   │       ├── PhaserGameBase.ts
│   │       ├── ChatMinigames.ts
│   │       └── chat-minigames/
│   │           └── ShapeSmashScene.ts
│   ├── public/
│   │   └── index.html
│   └── dist/                  # [GENERATED] Built files
│
├── submodules/                # Git submodules for external games
├── docs/                      # Documentation
└── tools/                     # Development utilities
```

### State Management Flow

**Backend → Frontend:**
```python
# Backend emits incremental updates
self.emit_state({'shape_added': shape_data})
```

**Frontend receives:**
```typescript
// GameManager passes update as-is (not merged)
this.currentGame.update(update)
```

**Why incremental?** Prevents transient events from persisting. See [STATE_MANAGEMENT.md](STATE_MANAGEMENT.md) for details.

---

## Available Games

### Chat Minigames Collection

A Phaser 3-based collection of interactive minigames. Currently includes:

#### 🎯 Shape Smash

Physics sandbox where viewers spawn shapes that bounce, collide, and interact!

**Chat Commands:**

| Command | Description | Cooldown |
|---------|-------------|----------|
| `!square` | Spawn a colored square | None |
| `!circle` | Spawn a colored circle | None |
| `!triangle` | Spawn a colored triangle | None |
| `!boost` | Launch all shapes upward | None |
| `!explode` | Shapes fly from center | None |
| `!clear` | Clear all shapes | Moderator only |

**Features:**
- ✅ Real-time physics (Phaser Arcade)
- ✅ Leaderboard scoring (hit targets for points)
- ✅ Username labels follow shapes
- ✅ Collision detection
- ✅ 10-color randomized palette

**Moderator Commands:**

| Command | Description |
|---------|-------------|
| `!nextgame` | Switch to next game in rotation |

<!--
🎥 **Gameplay Demo** (Placeholder)
Add gameplay footage or animated GIF here
-->

---

## Admin Panel

Access the admin panel at **`http://localhost:5000/admin`** to manage leaderboards.

### Features

- 📊 **Live Leaderboard** - Real-time score updates
- 👤 **Player Management** - Reset individual scores
- ✏️ **Score Editing** - Set custom scores
- 🗑️ **Bulk Actions** - Clear all scores with confirmation
- 📈 **Statistics** - Total players, scores, highest score

### Admin Actions

| Action | Description | Confirmation |
|--------|-------------|--------------|
| **Reset Player** | Set specific player to 0 points | Single prompt |
| **Set Score** | Manually set player score | None |
| **Clear All** | Delete all scores | Type "DELETE ALL" |

📖 **See Admin Panel documentation** *(in admin.html comments)*

---

## Development

### Development Mode (Hot-Reload)

Run backend and frontend in separate terminals for automatic reload:

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access at: `http://localhost:3000` (Vite dev server with HMR)

### Building for Production

```bash
cd frontend
npm run build
```

Outputs to `frontend/dist/` which Flask serves in production.

### Code Quality

```bash
# Frontend type checking
cd frontend
npm run type-check

# Backend linting
cd backend
pylint *.py
```

---

## Adding New Games

### Game Types

| Type | Description | Example |
|------|-------------|---------|
| **Standalone Game** | Complete game with own backend/frontend | Trivia Quiz |
| **Minigame Collection** | Multiple minigames sharing infrastructure | Chat Minigames |
| **Submodule Game** | External game repository | Community games |

### Option 1: Create a New Minigame Collection

Best for: Multiple related games sharing infrastructure

**1. Create directory structure:**
```bash
mkdir -p backend/games/my_collection/backend
mkdir -p backend/games/my_collection/minigames
```

**2. Create manifest (`backend/games/my_collection/game_manifest.json`):**
```json
{
  "id": "my_collection",
  "name": "My Game Collection",
  "version": "1.0.0",
  "description": "Collection of awesome minigames",
  "author": "your_name",

  "backend": {
    "entry_point": "game:MyCollectionGame"
  },

  "frontend": {
    "component": "MyCollection"
  },

  "minigames": [
    {
      "id": "minigame_1",
      "scene": "Minigame1Scene",
      "commands": ["command1", "command2"]
    }
  ]
}
```

**3. Create backend orchestrator (`backend/games/my_collection/backend/game.py`):**
```python
import sys
import os
from typing import Dict, Any, Callable

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_path)

from base_game import BaseGame

class MyCollectionGame(BaseGame):
    """Game collection orchestrator"""

    def get_title(self) -> str:
        return "My Game Collection"

    def get_game_id(self) -> str:
        return "my_collection"

    def get_commands(self) -> Dict[str, Callable]:
        return {
            'command1': self.handle_command1
        }

    def get_initial_state(self) -> Dict[str, Any]:
        return {'score': 0}

    def get_frontend_config(self) -> Dict[str, Any]:
        return {
            'component': 'MyCollection',
            'canvas_width': 1920,
            'canvas_height': 1080
        }

    def handle_command1(self, message):
        # Update state and emit to frontend
        self.emit_state({'action': 'command1_triggered'})
```

**4. Create Phaser scene (`frontend/src/games/my-collection/MyScene.ts`):**
```typescript
import Phaser from 'phaser';
import type { GameState } from '../../types';

export class MyScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MyScene' });
    }

    create() {
        // Initialize scene
        this.add.text(960, 540, 'My Game!', {
            fontSize: '48px',
            color: '#ffffff'
        }).setOrigin(0.5);
    }

    // Custom method called by container
    onStateUpdate(state: GameState) {
        if (state.action === 'command1_triggered') {
            // Handle state update
            console.log('Command 1 triggered!');
        }
    }
}
```

**5. Register in frontend (`frontend/src/games/registry.ts`):**
```typescript
import { MyCollection } from './MyCollection';

// Add to registry map
['MyCollection', MyCollection],
```

**6. Restart application** - Your game will auto-discover!

### Option 2: Add as Git Submodule

Best for: External games, community contributions

```bash
cd chat-games
git submodule add https://github.com/username/cool-game.git submodules/cool-game
git submodule update --init --recursive
```

Game must include valid `game_manifest.json` at root.

📖 **See [docs/PHASER_GAME_TEMPLATE.md](docs/PHASER_GAME_TEMPLATE.md) for full template**

---

## Deployment

### Production Checklist

- [ ] Build frontend: `npm run build`
- [ ] Set `DEBUG=False` in Flask config
- [ ] Use production WSGI server (gunicorn)
- [ ] Enable HTTPS for WebSockets
- [ ] Configure firewall for port 5000
- [ ] Set up process manager (systemd/supervisor)
- [ ] Configure Twitch OAuth for production domain
- [ ] Set up database backups

### Example Production Setup

```bash
# Install gunicorn
pip install gunicorn gevent-websocket

# Run with gunicorn
gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
         --workers 1 \
         --bind 0.0.0.0:5000 \
         app:app
```

---

## Troubleshooting

### Common Issues

<details>
<summary><strong>Frontend not loading?</strong></summary>

1. Ensure you built the frontend: `npm run build`
2. Check Flask is serving from `frontend/dist/`
3. Check browser console for errors
4. Verify Flask is running on port 5000
</details>

<details>
<summary><strong>Games not discovered?</strong></summary>

1. Validate `game_manifest.json` syntax (use JSON linter)
2. Check `backend.entry_point` matches class name exactly
3. Look for Python import errors in Flask console
4. Verify game is in `backend/games/` or `submodules/`
</details>

<details>
<summary><strong>SocketIO not connecting?</strong></summary>

1. Verify Flask server is running: `http://localhost:5000`
2. Check browser console for connection errors
3. Ensure CORS is enabled (default in development)
4. Check firewall isn't blocking port 5000
</details>

<details>
<summary><strong>Commands not working?</strong></summary>

1. Check Twitch bot connected (see Flask console)
2. Verify OAuth tokens are valid and not expired
3. Check command is registered in `get_commands()`
4. Ensure you're using correct prefix (default: `!`)
</details>

<details>
<summary><strong>Leaderboard not updating?</strong></summary>

1. Check database file exists: `backend/tokens.db`
2. Verify `player_scores` table was created
3. Check Flask console for database errors
4. Try admin panel health check: `/admin`
</details>

---

## Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-game`
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a Pull Request**

### Contribution Guidelines

- ✅ Follow existing code style
- ✅ Add documentation for new features
- ✅ Include example usage
- ✅ Test with multiple games
- ✅ Update relevant docs

### Creating New Games

**Requirements:**
- Valid `game_manifest.json`
- Backend class extends `BaseGame`
- Frontend class implements `GameComponent`
- README with setup instructions
- Example commands with descriptions

---

## Resources

- 📖 [Quick Start Guide](docs/QUICKSTART.md)
- 📖 [OBS Setup Instructions](docs/OBS_SETUP.md)
- 📖 [Phaser Game Template](docs/PHASER_GAME_TEMPLATE.md)
- 📖 [File Locations Reference](docs/FILE_LOCATIONS.md)
- 📖 [State Management Guide](STATE_MANAGEMENT.md)
- 🔗 [Phaser 3 Documentation](https://photonstorm.github.io/phaser3-docs/)
- 🔗 [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/)
- 🔗 [TwitchIO Documentation](https://twitchio.dev/)

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Credits

Built with ❤️ for the Twitch streaming community

**Technologies:**
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Vite](https://vitejs.dev/) - Frontend build tool
- [Phaser 3](https://phaser.io/) - Game framework
- [TwitchIO](https://github.com/TwitchIO/TwitchIO) - Twitch bot library
- [Socket.IO](https://socket.io/) - Real-time engine

---

> **Questions?** Open an issue or join our Discord *(link coming soon)*
