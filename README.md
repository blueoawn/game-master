# Shape Smash - Twitch Chat Game

An interactive game where your Twitch chat can spawn shapes that bounce around with physics!

## Complete Setup Guide

### Step 1: Create a Twitch Application

1. Go to https://dev.twitch.tv/console/apps
2. Click "Register Your Application"
3. Fill in:
   - **Name**: ShapeSmash (or any name you like)
   - **OAuth Redirect URLs**: `http://localhost:3000`
     - ⚠️ **IMPORTANT: Must be exactly this for local testing!**
     - Note: Twitch allows `http://localhost` (no HTTPS) for local development
     - For production/public use, you would need HTTPS
   - **Category**: Game Integration
4. Click "Create"
5. Click "Manage" on your new application
6. Copy the **Client ID**
7. Click "New Secret" and copy the **Client Secret** immediately (you won't see it again!)

### Step 2: Get Your Twitch User ID

1. Go to https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
2. Enter your Twitch username
3. Copy your User ID (it will be a number like `123456789`)

### Step 3: Install Dependencies

```bash
pip install pygame twitchio python-dotenv requests
```

### Step 4: Configure the Bot

1. **If you don't have a `.env` file yet**, copy `.env.example` to `.env` in the **git root** folder:
   ```bash
   cd "c:\Users\danie\OneDrive\Documents\git\stream tools"
   cp .env.example .env
   ```

2. Edit the `.env` file in the **root** of the stream-tools repository and add the Shape Smash configuration:
   
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

### Step 6: Run the Game!

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

**Note:** The `.env` file lives in the git root, not in `chat-games/`. This allows all stream tools to share the same configuration file.

## Production Deployment

**For Local Testing (Current Setup):**
- Uses `http://localhost:3000` - perfectly fine!
- Twitch explicitly allows localhost without HTTPS for development
- Run the game on your streaming PC

**For Production/Public Access:**
If you want to run this on a server or access it remotely, you would need:
1. A domain name with HTTPS (e.g., `https://yourdomain.com/callback`)
2. Update the redirect URI in your Twitch app

For most streamers, the local setup is all you need - just run it on your streaming PC!
