"""
Twitch bot integration for the new Flask architecture.
Adapted from original twitch_bot.py to work with the new system.
"""

import asyncio
import logging
import random
from typing import TYPE_CHECKING

import asqlite
import twitchio
from twitchio import eventsub
from twitchio.ext import commands

if TYPE_CHECKING:
    import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

LOGGER: logging.Logger = logging.getLogger("Bot")

# Load the .env file located one directory up from backend/
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

CLIENT_ID: str = os.getenv("CLIENT_ID") or ""
CLIENT_SECRET: str = os.getenv("CLIENT_SECRET") or ""
BOT_ID = os.getenv("BOT_ID") or ""
OWNER_ID = os.getenv("OWNER_ID") or ""

if not all([CLIENT_ID, CLIENT_SECRET, BOT_ID, OWNER_ID]):
    missing = [k for k in ("CLIENT_ID", "CLIENT_SECRET", "BOT_ID", "OWNER_ID") if not os.getenv(k)]
    raise RuntimeError(f"Missing required env variables: {', '.join(missing)} (looked in {env_path})")


class Bot(commands.AutoBot):
    def __init__(self, *, game_manager, token_database: asqlite.Pool, subs: list[eventsub.SubscriptionPayload]) -> None:
        self.game_manager = game_manager
        self.token_database = token_database
        self._handled_game_commands = set()  # Track commands we've already handled

        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            owner_id=OWNER_ID,
            prefix="!",
            subscriptions=subs,
            force_subscribe=True,
        )

    async def setup_hook(self) -> None:
        # Add our component which contains our commands...
        await self.add_component(MyComponent(self))

        # Add dynamic game commands component and initialize it
        self.game_commands = DynamicGameCommands(self)
        await self.add_component(self.game_commands)

        # Initialize commands from the active game
        if self.game_manager:
            await self.game_commands.refresh_commands()

    async def event_command_error(self, error: Exception) -> None:
        """Handle command errors - called when a command raises an exception"""
        # The error object contains the context
        if hasattr(error, '__context__') and isinstance(error.__context__, commands.CommandNotFound):
            actual_error = error.__context__
        elif isinstance(error, commands.CommandNotFound):
            actual_error = error
        else:
            # For other errors, log them
            LOGGER.error(f"Command error: {error}", exc_info=error)
            return

        # At this point we have a CommandNotFound error
        # Check if this was a game command that we already handled
        if self.game_manager:
            # Extract the command name from the error message
            error_msg = str(actual_error)
            # Error message format: 'The command "commandname" was not found.'
            if '"' in error_msg:
                cmd_name = error_msg.split('"')[1].lower()
                active_commands = self.game_manager.get_active_commands()
                if cmd_name in active_commands:
                    # This was a game command, already handled - suppress the error
                    return

        # If we get here, it's a real CommandNotFound error - log it
        LOGGER.warning(f"Command not found: {actual_error}")

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        if payload.user_id == self.bot_id:
            # We usually don't want subscribe to events on the bots channel...
            return

        # A list of subscriptions we would like to make to the newly authorized channel...
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id),
        ]

        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.warning("Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id)

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)


class MyComponent(commands.Component):
    """Example component with simple commands"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

    @commands.command()
    async def hi(self, ctx: commands.Context) -> None:
        """Command that replies to the invoker with Hi <name>!"""
        await ctx.reply(f"Hi {ctx.chatter}!")

    @commands.command()
    async def say(self, ctx: commands.Context, *, message: str) -> None:
        """Command which repeats what the invoker sends."""
        await ctx.send(message)

    @commands.command()
    async def add(self, ctx: commands.Context, left: int, right: int) -> None:
        """Command which adds to integers together."""
        await ctx.reply(f"{left} + {right} = {left + right}")

    @commands.command()
    async def choice(self, ctx: commands.Context, *choices: str) -> None:
        """Command which takes in an arbitrary amount of choices and randomly chooses one."""
        await ctx.reply(f"You provided {len(choices)} choices, I choose: {random.choice(choices)}")

    # === Admin Commands for Score Management ===

    @commands.is_elevated()
    @commands.command()
    async def resetscores(self, ctx: commands.Context) -> None:
        """Clear all player scores (moderator/broadcaster only)."""
        # TODO: Implement database clearing logic
        await ctx.reply("⚠️ Command stub: !resetscores - This will clear all player scores. Use the web admin panel at http://localhost:5000/admin")

    @commands.is_elevated()
    @commands.command()
    async def resetscore(self, ctx: commands.Context, username: str) -> None:
        """Reset a specific player's score to 0 (moderator/broadcaster only)."""
        # TODO: Implement database reset logic for specific player
        await ctx.reply(f"⚠️ Command stub: !resetscore {username} - This will reset {username}'s score. Use the web admin panel at http://localhost:5000/admin")

    @commands.is_elevated()
    @commands.command()
    async def setscore(self, ctx: commands.Context, username: str, score: int) -> None:
        """Set a specific player's score (moderator/broadcaster only)."""
        # TODO: Implement database set score logic
        await ctx.reply(f"⚠️ Command stub: !setscore {username} {score} - This will set {username}'s score to {score}. Use the web admin panel at http://localhost:5000/admin")


class DynamicGameCommands(commands.Component):
    """Component that dynamically routes commands to the active game"""

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.Component.listener()
    async def event_message(self, message: twitchio.ChatMessage) -> None:
        """Listen for messages and route game commands dynamically"""
        # Only process messages that start with the command prefix
        if not message.text.startswith('!'):
            return

        # Parse command name (first word without !)
        parts = message.text[1:].split()
        if not parts:
            return

        cmd_name = parts[0].lower()

        # Check if this command belongs to the active game
        if self.bot.game_manager:
            active_commands = self.bot.game_manager.get_active_commands()
            if cmd_name in active_commands:
                try:
                    # Call the game's command handler
                    active_commands[cmd_name](message)
                    active_game = self.bot.game_manager.get_active_game()
                    if active_game:
                        LOGGER.info(f"Routed !{cmd_name} to active game: {active_game.get_title()}")
                except Exception as e:
                    LOGGER.error(f"Error executing game command !{cmd_name}: {e}")

    async def refresh_commands(self):
        """Refresh is not needed since we route dynamically"""
        if self.bot.game_manager and self.bot.game_manager.get_active_game():
            active_game = self.bot.game_manager.get_active_game()
            active_commands = self.bot.game_manager.get_active_commands()
            LOGGER.info(f"Active game: {active_game.get_title()}")
            LOGGER.info(f"Available commands: {', '.join(['!' + cmd for cmd in active_commands.keys()])}")

    @commands.is_elevated()
    @commands.command()
    async def nextgame(self, ctx: commands.Context) -> None:
        """Switch to the next game (moderator/broadcaster only)."""
        if not self.bot.game_manager:
            return

        active_game = self.bot.game_manager.get_active_game()
        old_game = active_game.get_title() if active_game else "None"
        self.bot.game_manager.next_game()
        new_game = self.bot.game_manager.get_active_game()
        new_game_title = new_game.get_title() if new_game else "None"

        await ctx.send(f"Switched from {old_game} to {new_game_title}!")


async def setup_database(db: asqlite.Pool) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    """Setup database and fetch existing tokens"""
    async with db.acquire() as connection:
        # Create tokens table
        await connection.execute("""CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)""")

        # Create player_scores table for leaderboard persistence
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS player_scores(
                username TEXT PRIMARY KEY,
                score INTEGER NOT NULL DEFAULT 0,
                game_name TEXT NOT NULL DEFAULT 'ShapeSmash',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Fetch any existing tokens...
        rows: list['sqlite3.Row'] = await connection.fetchall("""SELECT * from tokens""")

        tokens: list[tuple[str, str]] = []
        subs: list[eventsub.SubscriptionPayload] = []

        for row in rows:
            tokens.append((row["token"], row["refresh"]))

            if row["user_id"] == BOT_ID:
                continue

            subs.extend([eventsub.ChatMessageSubscription(broadcaster_user_id=row["user_id"], user_id=BOT_ID)])

    return tokens, subs


def main(game_manager=None) -> None:
    """Main entry point for the Bot (standalone mode)"""
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with asqlite.create_pool("tokens.db") as tdb:
            tokens, subs = await setup_database(tdb)

            async with Bot(game_manager=game_manager, token_database=tdb, subs=subs) as bot:
                for pair in tokens:
                    await bot.add_token(*pair)

                await bot.start(load_tokens=False)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt")


if __name__ == "__main__":
    main()
