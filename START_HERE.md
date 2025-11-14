# 🎮 START HERE - Your Complete Twitch Chat Game System

## What You Have

A **professional, modular Twitch chat game platform** with:

✅ **Phaser 3** - Professional HTML5 game framework
✅ **Flask Backend** - Python server handling Twitch commands
✅ **TypeScript Frontend** - Type-safe, modern JavaScript
✅ **OBS Ready** - Works as browser source
✅ **Modular** - Easy to add new games
✅ **Real-time** - WebSocket communication

## Quick Start (First Time)

### 1. Install Dependencies

```bash
# Install backend
cd backend
pip install -r requirements.txt

# Install frontend (includes Phaser 3!)
cd ../frontend
npm install
```

### 2. Build Frontend

```bash
cd frontend
npm run build
```

### 3. Start the Server

```bash
cd backend
python app.py
```

### 4. Open in Browser

Visit: **http://localhost:5000**

You should see Shape Smash running!

### 5. Add to OBS

See [OBS_SETUP.md](OBS_SETUP.md) for detailed instructions.

Quick version:
1. Add **Browser Source** in OBS
2. URL: `http://localhost:5000`
3. Width: `1920`, Height: `1080`
4. Done!

### 6. Test Commands in Twitch Chat

- `!square` - Spawn a square
- `!circle` - Spawn a circle
- `!triangle` - Spawn a triangle
- `!boost` - Boost shapes up
- `!explode` - Explode from center
- `!clear` - Clear all (mod only)

## Development Workflow

### Making Changes to Frontend

```bash
cd frontend
npm run dev
```

This starts Vite dev server with hot-reload on **http://localhost:3000**

### Making Changes to Backend

Just restart:
```bash
cd backend
python app.py
```

### Building for Production

```bash
cd frontend
npm run build
```

## Adding Your Own Games

### Option 1: Use the Template

Follow [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md) for step-by-step guide.

### Option 2: Quick Summary

1. **Create folders**: `games/builtin/my_game/backend` and `frontend`
2. **Create manifest**: `game_manifest.json`
3. **Python backend**: Handles Twitch commands
4. **TypeScript frontend**: Phaser 3 game rendering
5. **Register**: Add to `frontend/src/games/registry.ts`
6. **Build & test!**

## File Structure

```
chat-games/
├── backend/              # Flask + Twitch Bot
│   ├── app.py           # Main server
│   ├── base_game.py     # Game base class
│   └── twitch_bot.py    # Twitch integration
│
├── frontend/            # TypeScript + Phaser 3
│   ├── src/
│   │   ├── games/
│   │   │   ├── PhaserGameBase.ts      # Base for Phaser games
│   │   │   ├── ShapeSmashPhaser.ts    # Shape Smash (Phaser)
│   │   │   └── registry.ts            # Register games here
│   │   └── main.ts
│   └── dist/            # Built files (Flask serves these)
│
└── games/builtin/       # Your game modules
    └── shape_smash/
        ├── game_manifest.json
        ├── backend/game.py
        └── frontend/ (code in frontend/src/games/)
```

## Documentation

| Document | Purpose |
|----------|---------|
| **[START_HERE.md](START_HERE.md)** | This file - overview |
| **[QUICKSTART.md](QUICKSTART.md)** | Fast setup guide |
| **[README_NEW.md](README_NEW.md)** | Complete documentation |
| **[OBS_SETUP.md](OBS_SETUP.md)** | OBS browser source setup |
| **[PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md)** | How to create new games |
| **[FILE_LOCATIONS.md](FILE_LOCATIONS.md)** | Where everything is |
| **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** | Technical architecture details |

## Architecture Overview

```
Twitch Chat
    ↓
Twitch Bot (Python)
    ↓
Game Command Handler (Python)
    ↓
Flask-SocketIO
    ↓
WebSocket
    ↓
TypeScript Frontend
    ↓
Phaser 3 Game Engine
    ↓
Browser / OBS
```

## Key Features

### For You (Developer)

- **Phaser 3** - Professional game engine with physics, sprites, animations
- **TypeScript** - Type safety and autocomplete
- **Hot-reload** - See changes instantly during development
- **Modular** - Each game is self-contained
- **Manifest-based** - Games auto-discover themselves

### For Your Stream

- **OBS Integration** - Works as browser source
- **Real-time Updates** - Instant command response
- **Interactive** - Chat controls the game
- **Multiple Games** - Switch between games with `!nextgame`

## Common Tasks

### Install Everything
```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### Build Frontend
```bash
cd frontend && npm run build
```

### Run Production
```bash
cd backend && python app.py
# Open http://localhost:5000
```

### Run Development (Hot-Reload)
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && npm run dev
# Open http://localhost:3000
```

### Add to OBS
```
Browser Source → URL: http://localhost:5000
Width: 1920, Height: 1080
```

### Create New Game
See [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md)

## Troubleshooting

**Frontend not loading?**
- Run `cd frontend && npm run build`
- Check `frontend/dist/` exists

**Commands not working?**
- Check Twitch bot is connected (backend console)
- Verify `.env` file in `stream-tools/`

**OBS shows blank?**
- Check Flask is running on port 5000
- Test URL in regular browser first

**TypeScript errors?**
- Run `cd frontend && npm run check`

## Next Steps

1. **Get it running** - Follow Quick Start above
2. **Add to OBS** - See [OBS_SETUP.md](OBS_SETUP.md)
3. **Test commands** - Try `!square` in Twitch chat
4. **Create your first game** - Use [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md)
5. **Customize** - Make it your own!

## Resources

- [Phaser 3 Documentation](https://photonstorm.github.io/phaser3-docs/)
- [Phaser 3 Examples](https://phaser.io/examples)
- [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/)
- [TwitchIO Docs](https://twitchio.dev/)

## Need Help?

1. Check [QUICKSTART.md](QUICKSTART.md)
2. Read [OBS_SETUP.md](OBS_SETUP.md) if OBS issues
3. Review [FILE_LOCATIONS.md](FILE_LOCATIONS.md) for paths
4. See [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md) for examples

---

**You're all set!** Run the Quick Start above and you'll have a working game system in minutes. 🚀
