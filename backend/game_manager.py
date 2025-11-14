"""
Game Manager - Handles game cycling and coordination between games and the bot.
Updated for Flask + SocketIO architecture.
"""
from pathlib import Path
from typing import Optional
import logging

from game_loader import GameLoader
from base_game import BaseGame

logger = logging.getLogger(__name__)


class GameManager:
    """Manages game lifecycle and switching"""

    def __init__(self, socketio):
        """
        Initialize the game manager.

        Args:
            socketio: Flask-SocketIO instance for real-time communication
        """
        self.socketio = socketio
        self.games = {}  # game_id -> manifest mapping
        self.active_game: Optional[BaseGame] = None
        self.active_game_id: Optional[str] = None

        # Initialize game loader
        base_path = Path(__file__).parent.parent
        search_paths = [
            base_path / "games" / "builtin",
            base_path / "submodules"
        ]
        self.loader = GameLoader(search_paths)

        logger.info("GameManager initialized")

    def discover_games(self):
        """Discover and register all available games"""
        manifests = self.loader.discover_games()
        logger.info(f"Found {len(manifests)} games")

        # Store manifests
        for manifest in manifests:
            self.games[manifest['id']] = manifest

    def load_game(self, game_id: str):
        """
        Load and activate a game.

        Args:
            game_id: Game identifier to load

        Returns:
            BaseGame: The loaded game instance

        Raises:
            ValueError: If game not found
        """
        # Unload current game
        if self.active_game:
            logger.info(f"Ending game: {self.active_game.get_title()}")
            self.active_game.on_game_end()

        # Load new game
        self.active_game = self.loader.load_game(game_id, self.socketio)
        self.active_game_id = game_id
        self.active_game.room_id = 'main_room'

        # Initialize game
        self.active_game.reset()
        self.active_game.on_game_start()

        # Emit game loaded event to frontend
        frontend_config = self.loader.get_frontend_config(game_id)
        self.socketio.emit('game_loaded', {
            'gameId': game_id,
            'title': self.active_game.get_title(),
            'initialState': self.active_game.get_initial_state(),
            'config': frontend_config
        }, room='main_room')

        logger.info(f"Loaded and started game: {self.active_game.get_title()}")
        return self.active_game

    def next_game(self):
        """
        Cycle to the next game in the list.
        Resets the new game's state.
        """
        if len(self.games) <= 1:
            logger.warning("Only one game registered, cannot cycle")
            return

        # Get list of game IDs
        game_ids = list(self.games.keys())

        # Find current index
        if self.active_game_id in game_ids:
            current_index = game_ids.index(self.active_game_id)
            next_index = (current_index + 1) % len(game_ids)
        else:
            next_index = 0

        # Load next game
        next_game_id = game_ids[next_index]
        self.load_game(next_game_id)

    def get_active_game(self) -> Optional[BaseGame]:
        """
        Get the currently active game.

        Returns:
            BaseGame: The active game instance, or None if no game loaded
        """
        return self.active_game

    def get_active_commands(self) -> dict:
        """
        Get the command dictionary from the active game.

        Returns:
            dict: Command name -> callback function mapping
        """
        if self.active_game:
            return self.active_game.get_commands()
        return {}

    def update(self, delta_time: float = 0.016):
        """
        Update the active game (server-side game loop).

        Args:
            delta_time: Time since last update in seconds
        """
        if self.active_game:
            self.active_game.update(delta_time)

            # Check if game has signaled it's finished
            if self.active_game.finish():
                logger.info(f"{self.active_game.get_title()} has finished!")
                self.next_game()
