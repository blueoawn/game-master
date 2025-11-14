# Twitch Chat Games v2.0

A modular multi-game platform where your Twitch chat can play interactive games! Now with a **Flask backend** and **TypeScript frontend** architecture for better performance and easier game development.

## 🎯 New Architecture

### Backend (Python)
- **Flask + Flask-SocketIO**: Real-time WebSocket communication
- **TwitchBot**: Handles Twitch chat integration
- **GameManager**: Manages game lifecycle and switching
- **BaseGame**: Abstract class for all games with state management

### Frontend (TypeScript)
- **Vite**: Fast build tooling
- **Socket.IO Client**: Real-time state updates
- **Canvas Rendering**: Smooth 60 FPS animations
- **GameRegistry**: Dynamic game component loading

### Games
Each game consists of:
- **Backend (Python)**: Command handlers, game logic, state management
- **Frontend (TypeScript)**: Rendering, animations, physics
- **Manifest**: JSON configuration for auto-discovery

## 📁 New Folder Structure

```
chat-games/
├── backend/
│   ├── app.py                 # Flask application
│   ├── base_game.py           # BaseGame abstract class
│   ├── game_loader.py         # Game discovery system
│   ├── game_manager.py        # Game lifecycle management
│   ├── twitch_bot.py          # Twitch integration
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── main.ts           # Entry point
│   │   ├── socket.ts         # SocketIO client
│   │   ├── gameManager.ts    # Frontend game coordination
│   │   ├── types.ts          # TypeScript types
│   │   └── games/
│   │       ├── registry.ts   # Game component registry
│   │       └── ShapeSmash.ts # Shape Smash frontend
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── games/
│   └── builtin/
│       └── shape_smash/
│           ├── game_manifest.json
│           ├── backend/
│           │   └── game.py
│           └── frontend/
│               └── ShapeSmash.ts
│
└── submodules/               # Add games here as git submodules!
```

## 🚀 Setup Instructions

### 1. Install Python Dependencies

```bash
cd chat-games/backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd chat-games/frontend
npm install
```

### 3. Configure Environment Variables

Make sure your `.env` file exists in the root of `stream-tools/`:

```
CLIENT_ID=your_twitch_client_id
CLIENT_SECRET=your_twitch_client_secret
BOT_ID=your_bot_user_id
OWNER_ID=your_user_id
```

### 4. Build Frontend (Production)

```bash
cd chat-games/frontend
npm run build
```

This creates `frontend/dist/` which Flask will serve.

### 5. Start the Application

```bash
cd chat-games/backend
python app.py
```

This starts:
- Flask server on `http://localhost:5000`
- SocketIO WebSocket server
- Twitch bot in background thread

### 6. Access the Application

Open your browser to: `http://localhost:5000`

## 🎮 Available Games

### Shape Smash
Interactive physics sandbox where viewers spawn shapes that bounce and collide!

**Chat Commands:**
- `!square` - Spawn a square
- `!circle` - Spawn a circle
- `!triangle` - Spawn a triangle
- `!boost` - Boost all shapes upward
- `!explode` - Make shapes explode outward from center
- `!clear` - Clear all shapes (moderator only)

**Moderator Commands:**
- `!nextgame` - Switch to the next game

## 🔧 Development Mode

For development with hot-reload:

**Terminal 1 - Backend:**
```bash
cd chat-games/backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd chat-games/frontend
npm run dev
```

Then open `http://localhost:3000` (Vite dev server with auto-refresh)

## ➕ Adding New Games

### Option 1: Built-in Game

1. **Create game folder:**
   ```bash
   mkdir -p games/builtin/my_game/backend
   mkdir -p games/builtin/my_game/frontend
   ```

2. **Create manifest** (`games/builtin/my_game/game_manifest.json`):
   ```json
   {
     "id": "my_game",
     "name": "My Awesome Game",
     "version": "1.0.0",
     "description": "A cool new game",
     "author": "your_name",

     "backend": {
       "entry_point": "game:MyGame"
     },

     "frontend": {
       "component": "MyGame",
       "entry_point": "frontend/MyGame.ts"
     },

     "config": {
       "setting1": "value1"
     },

     "commands": [
       {"name": "command1", "description": "Does something"}
     ]
   }
   ```

3. **Create backend** (`games/builtin/my_game/backend/game.py`):
   ```python
   import sys
   from pathlib import Path

   # Add backend to path
   backend_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "backend"
   sys.path.insert(0, str(backend_path))

   from base_game import BaseGame

   class MyGame(BaseGame):
       def get_title(self) -> str:
           return "My Awesome Game"

       def get_game_id(self) -> str:
           return "my_game"

       def get_commands(self) -> dict:
           return {
               'command1': self.handle_command1
           }

       def get_initial_state(self) -> dict:
           return {'score': 0}

       def get_frontend_config(self) -> dict:
           return {
               'component': 'MyGame',
               'canvas_width': 1920,
               'canvas_height': 1080
           }

       def handle_command1(self, message):
           # Update state and emit to frontend
           self.update_state({'score': self.game_state.get('score', 0) + 1})
   ```

4. **Create frontend** (`games/builtin/my_game/frontend/MyGame.ts`):
   ```typescript
   import type { GameComponent, GameState, GameConfig } from '../../../frontend/src/types';

   export class MyGame implements GameComponent {
       private container: HTMLElement;
       private canvas: HTMLCanvasElement;
       private ctx: CanvasRenderingContext2D;

       constructor(container: HTMLElement, config: GameConfig) {
           this.container = container;
           this.canvas = document.createElement('canvas');
           this.ctx = this.canvas.getContext('2d')!;
           container.appendChild(this.canvas);
       }

       init(initialState: GameState): void {
           // Initialize game
       }

       update(state: GameState): void {
           // Update and render
       }

       destroy(): void {
           // Cleanup
       }
   }
   ```

5. **Register in frontend** (`frontend/src/games/registry.ts`):
   ```typescript
   import { MyGame } from '../../games/builtin/my_game/frontend/MyGame';

   // Add to registry
   ['MyGame', MyGame],
   ```

6. **Restart the application** - Your game will be auto-discovered!

### Option 2: Submodule Game

Add an external game repository as a git submodule:

```bash
cd chat-games
git submodule add https://github.com/username/cool-game.git submodules/cool-game
```

As long as the game has a `game_manifest.json` file, it will be auto-discovered!

## 📡 Communication Flow

```
Twitch Chat → TwitchBot → Game Command Handler → Game State Update
                                                          ↓
                                                  emit_state()
                                                          ↓
                                              Flask-SocketIO Server
                                                          ↓
                                              Socket.IO WebSocket
                                                          ↓
                                          TypeScript Frontend GameManager
                                                          ↓
                                              Game Component update()
                                                          ↓
                                                  Canvas Rendering
```

## 🎨 Game State Management

**Backend (Python):**
```python
# Update state and emit to frontend
self.update_state({
    'score': 100,
    'event': 'player_scored',
    'player_name': username
})
```

**Frontend (TypeScript):**
```typescript
update(state: GameState): void {
    if (state.event === 'player_scored') {
        this.showAnimation(state.player_name);
    }
    this.score = state.score;
    this.render();
}
```

## 🔍 Debugging

Access debug tools in browser console:
```javascript
// Available globally
window.gameManager  // Frontend game manager
window.socket       // Socket.IO client

// Load a different game
window.gameManager.requestGameSwitch('my_game')
```

## 📊 Architecture Benefits

✅ **Separation of Concerns**: Backend handles logic, frontend handles rendering
✅ **Real-time Updates**: WebSocket communication for instant state sync
✅ **Modular Games**: Easy to add/remove games via submodules
✅ **Type Safety**: TypeScript prevents runtime errors
✅ **Auto-Discovery**: Games self-register via manifests
✅ **Hot-Reload**: Fast development iteration
✅ **Scalable**: Can run on separate servers if needed

## 🐛 Troubleshooting

**Frontend not loading?**
- Make sure you ran `npm run build` in `frontend/`
- Check Flask is serving from `frontend/dist/`

**Games not discovered?**
- Check `game_manifest.json` is valid JSON
- Ensure `backend/entry_point` matches class name
- Look for errors in Flask console

**SocketIO not connecting?**
- Verify Flask is running on port 5000
- Check browser console for connection errors
- Ensure CORS is enabled (it is by default)

**Commands not working?**
- Make sure Twitch bot is connected (check console)
- Verify OAuth tokens are valid
- Check command is registered in game's `get_commands()`

## 🤝 Contributing

We welcome new games! Create a repository with the structure above and share it as a submodule.

**Requirements for game repositories:**
- Valid `game_manifest.json`
- Backend class inheriting from `BaseGame`
- Frontend class implementing `GameComponent`
- README with game instructions

## 📝 License

MIT

## 🎉 Credits

Built with ❤️ for the Twitch streaming community
