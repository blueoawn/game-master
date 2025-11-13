# Twitch Chat Games

A multi-game platform where your Twitch chat can play interactive games! Currently features Shape Smash with more games coming soon.

## Complete Setup Guide

### Step 1: Create a Twitch Application

1. Go to https://dev.twitch.tv/console/apps
2. Click "Register Your Application"
3. Do the oauth thing for your bot so it can join your channel, uhh, I followed this: [quickstart guide](https://twitchio.dev/en/latest/getting-started/quickstart.html)
4. Once you have tokens, you're good to go.

### Step 2: Install Dependencies

```bash
pip install pygame twitchio python-dotenv requests
```

### Step 3: Configure the Bot

1. **If you don't have a `.env` file yet**, copy `.env.example` to `.env` in the **git root** folder:
   ```bash
   cd "\stream tools"
   cp .env.example .env
   ```

2. Edit the `.env` file in the **root** of the [stream-tools](https://github.com/blueoawn/) repository and add the fields for the twitch bot:
   
   ```
   CLIENT_ID =
   CLIENT_SECRET =
   BOT_ID =
   OWNER_ID = 
   ```

   **Note:** The `.env` file is in the git root (`stream-tools/.env`), not in the `chat-games/` folder. This allows all tools in the repo to share the same configuration.

**Required Scopes:**
- `user:read:chat` - Read chat messages
- `user:bot` - Act as a bot
- `channel:bot` - Bot in channel
- `moderator:read:chatters` - Read chatters list

### Step 4: Run the Games!

```bash
cd chat-games
python main.py
```

The game window will open and the bot will connect to your Twitch chat!

**Note:** You can run this from anywhere in the repo - the game will automatically find the `.env` file in the git root.

## Available Games

### Shape Smash
An interactive physics sandbox where viewers spawn shapes that bounce and collide!

**Chat Commands:**
- `!square` - Spawns a square
- `!circle` - Spawns a circle
- `!triangle` - Spawns a triangle
- `!boost` - Boost all your shapes upward
- `!spin` - Make shapes spin wildly
- `!explode` - Make shapes explode outward from center
- `!gravity` - Toggle gravity direction
- `!clear` - Clear all shapes (moderator only)

### More Games Coming Soon!
The architecture now supports multiple games that can cycle automatically.

## Global Commands

- `!nextgame` - Switch to the next game (moderator/broadcaster only)

## Architecture Overview

The application is built with a modular architecture that makes it easy to add new games:

### File Structure

```
stream-tools/              # Git root
├── .env                   # Your configuration (shared by all tools, not in git)
├── .env.example           # Example configuration for all tools
├── .gitignore             # Git ignore file
└── chat-games/            # Multi-game platform
    ├── main.py                # Main entry point (run this!)
    ├── game_manager.py        # Manages game cycling and canvas
    ├── twitch_bot.py          # Twitch bot with dynamic command loading
    ├── shape_smash.py         # Legacy entry point (deprecated)
    ├── assets/                # Shared resources across all games
    │   ├── shapes.py          # Shape classes with physics
    │   ├── physics.py         # Physics constants
    │   └── colors.py          # Color definitions
    ├── games/                 # Individual game modules
    │   ├── base_game.py       # Abstract base class for all games
    │   └── shape_smash/       # Shape Smash game
    │       └── game.py        # ShapeSmashGame implementation
    ├── requirements.txt       # Python dependencies
    ├── tokens.db              # OAuth tokens (not in git, auto-generated)
    └── README.md              # This file
```

## Adding New Games

To add a new game to the platform:

1. **Create a new game folder** in `games/`:
   ```bash
   mkdir games/my_new_game
   ```

2. **Create your game class** inheriting from `BaseGame`:
   ```python
   # games/my_new_game/game.py
   from games.base_game import BaseGame

   class MyNewGame(BaseGame):
       def get_title(self) -> str:
           return "My New Game"

       def get_commands(self) -> dict:
           return {
               'command1': self.handle_command1,
               'command2': self.handle_command2
           }

       def update(self):
           # Game logic here
           pass

       def draw(self, screen):
           # Drawing code here
           pass

       def reset(self):
           # Reset game state
           pass
   ```

3. **Register your game** in [main.py](main.py):
   ```python
   from games.my_new_game import MyNewGame

   # In main():
   my_game = MyNewGame(game_manager.get_font(), game_manager.get_title_font())
   game_manager.register_game(my_game)
   ```

4. **That's it!** Your game is now part of the rotation and its commands will automatically be available when it's active.

## Future Plans

- [ ] Player stats database (track wins, participation, etc.)
- [ ] Auto-cycling based on game finish() signal
- [ ] More games!
- [ ] Custom game timers
- [ ] Game voting system
