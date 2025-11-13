# Shape Smash - Twitch Chat Game

An interactive game where your Twitch chat can spawn shapes that bounce around with physics!

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

### Step 4: Run the Game!

```bash
cd chat-games
python shape_smash.py
```

The game window will open and the bot will connect to your Twitch chat!

**Note:** You can run this from anywhere in the repo - the game will automatically find the `.env` file in the git root.

## Chat Commands

Once the game is running, viewers can use these commands:

- `!square` - Spawns a square
- `!circle` - Spawns a circle
- `!triangle` - Spawns a triangle

## Game Features

- **Physics**: Shapes fall with gravity, bounce off walls, and slow down with friction
- **Usernames**: Each shape displays who spawned it
- **Shape Limit**: Maximum 50 shapes to prevent lag
- **Random Colors**: Each shape gets a random color
- **Multiple Shapes**: Square, Circle, and Triangle types

## File Structure

```
stream-tools/              # Git root
├── .env                   # Your configuration (shared by all tools, not in git)
├── .env.example           # Example configuration for all tools
├── .gitignore             # Git ignore file
└── chat-games/            # Shape Smash game folder
    ├── shape_smash.py         # Main game file
    ├── shapes.py              # Shape classes and physics
    ├── twitch_bot.py          # Twitch bot integration
    ├── requirements.txt       # Python dependencies
    ├── tokens.db              # OAuth tokens (not in git, auto-generated)
    └── README.md              # This file
```
