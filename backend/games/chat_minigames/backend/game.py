"""
Chat Minigames - Collection Orchestrator
Manages multiple minigames using Phaser's scene manager
"""
import sys
import os
import importlib
import logging
from typing import Dict, Any, Callable

# Add backend to path for BaseGame import
# Path: backend/games/chat_minigames/backend/game.py → ../../ → backend/
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_path)

from base_game import BaseGame

logger = logging.getLogger(__name__)


class ChatMinigamesGame(BaseGame):
    """
    Orchestrator for chat minigames collection.
    Routes commands to active minigame and manages scene switching.
    """

    def __init__(self, socketio=None):
        super().__init__(socketio)
        self.active_minigame = None
        self.minigames = {}
        self._load_minigames()

    def _load_minigames(self):
        """Dynamically load all minigame modules"""
        minigames_dir = os.path.join(os.path.dirname(__file__), '../minigames')

        # Import shape_smash minigame
        try:
            # Add minigames directory to path
            sys.path.insert(0, minigames_dir)

            # Import shape_smash module
            shape_smash_module = importlib.import_module('shape_smash')

            # Create instance
            self.minigames['shape_smash'] = shape_smash_module.ShapeSmashMinigame(self)
            logger.info("✅ Loaded minigame: shape_smash")

        except Exception as e:
            logger.error(f"❌ Failed to load shape_smash minigame: {e}")
            raise

        # Set default active minigame
        if self._manifest:
            default_game = self._manifest.get('config', {}).get('default_minigame', 'shape_smash')
            self.active_minigame = self.minigames.get(default_game)
        else:
            # Fallback if no manifest
            self.active_minigame = self.minigames.get('shape_smash')

    # === METADATA ===

    def get_title(self) -> str:
        """Return the game's display title"""
        return "Chat Minigames"

    def get_game_id(self) -> str:
        """Return unique game identifier"""
        return "chat_minigames"

    # === COMMANDS ===

    def get_commands(self) -> Dict[str, Callable]:
        """
        Aggregate commands from all minigames plus collection-level commands
        """
        commands = {}

        # Add collection-level commands
        commands['minigame'] = self.switch_minigame

        # Add all commands from all minigames
        for minigame_id, minigame in self.minigames.items():
            minigame_commands = minigame.get_commands()
            commands.update(minigame_commands)

        return commands

    # === STATE MANAGEMENT ===

    def get_initial_state(self) -> Dict[str, Any]:
        """Return initial state including active scene"""
        state = {
            'active_scene': self._get_scene_name(self.active_minigame),
            'available_minigames': list(self.minigames.keys())
        }

        # Add active minigame's initial state
        if self.active_minigame:
            minigame_state = self.active_minigame.get_initial_state()
            state.update(minigame_state)

        return state

    def _get_scene_name(self, minigame) -> str:
        """Get the Phaser scene name for a minigame"""
        if minigame is None:
            return 'ShapeSmashScene'  # Default fallback

        # Get from manifest if available
        if self._manifest and 'minigames' in self._manifest:
            for mg in self._manifest['minigames']:
                if mg['id'] == minigame.get_minigame_id():
                    return mg.get('scene', 'ShapeSmashScene')

        return 'ShapeSmashScene'  # Default fallback

    # === MINIGAME MANAGEMENT ===

    def switch_minigame(self, message):
        """
        Switch to a different minigame
        Usage: !minigame <name>
        """
        parts = message.content.split()
        if len(parts) < 2:
            logger.warning("No minigame name provided")
            return

        minigame_name = parts[1].lower()

        if minigame_name not in self.minigames:
            logger.warning(f"Unknown minigame: {minigame_name}")
            return

        # Call cleanup on old minigame
        if self.active_minigame:
            self.active_minigame.on_deactivate()

        # Switch to new minigame
        self.active_minigame = self.minigames[minigame_name]

        # Activate new minigame
        self.active_minigame.on_activate()

        # Emit scene switch
        self.emit_state({
            'event': 'switch_scene',
            'active_scene': self._get_scene_name(self.active_minigame),
            'minigame': minigame_name
        })

        logger.info(f"Switched to minigame: {minigame_name}")

    # === LIFECYCLE ===

    def on_game_start(self):
        """Called when game becomes active"""
        if self.active_minigame:
            self.active_minigame.on_activate()
        logger.info("Chat Minigames started")

    def on_game_end(self):
        """Called when game is being switched away from"""
        if self.active_minigame:
            self.active_minigame.on_deactivate()
        logger.info("Chat Minigames ended")

    # === FRONTEND INFO ===

    def get_frontend_config(self) -> Dict[str, Any]:
        """Return frontend configuration"""
        config = {
            'component': 'ChatMinigames',
            'canvas_width': 1920,
            'canvas_height': 1080
        }

        # Override with manifest config if available
        if self._manifest and 'config' in self._manifest:
            config.update(self._manifest['config'])

        return config
