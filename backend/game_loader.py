"""
Game discovery and loading system using manifest files.
Automatically discovers games from specified directories.
"""
import json
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from base_game import BaseGame

logger = logging.getLogger(__name__)


class GameLoader:
    """Discovers and loads games from manifests"""

    def __init__(self, search_paths: List[Path]):
        """
        Initialize loader with paths to search for games.

        Args:
            search_paths: Directories to search (e.g., builtin/, submodules/)
        """
        self.search_paths = search_paths
        self.games: Dict[str, Dict[str, Any]] = {}

    def discover_games(self) -> List[Dict[str, Any]]:
        """
        Scan search paths for game manifests.

        Returns:
            List of game metadata dictionaries
        """
        discovered = []

        for search_path in self.search_paths:
            if not search_path.exists():
                logger.warning(f"Search path does not exist: {search_path}")
                continue

            # Look for game_manifest.json in subdirectories
            for item in search_path.iterdir():
                if not item.is_dir():
                    continue

                manifest_path = item / "game_manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, encoding='utf-8') as f:
                            manifest = json.load(f)

                        # Validate required fields
                        required = ['id', 'name', 'backend', 'frontend']
                        missing = [field for field in required if field not in manifest]
                        if missing:
                            logger.error(f"Manifest {manifest_path} missing fields: {missing}")
                            continue

                        manifest['_path'] = item
                        discovered.append(manifest)
                        self.games[manifest['id']] = manifest

                        logger.info(f"Discovered game: {manifest['name']} ({manifest['id']})")
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in {manifest_path}: {e}")
                    except Exception as e:
                        logger.error(f"Error loading manifest {manifest_path}: {e}")

        logger.info(f"Discovered {len(discovered)} games total")
        return discovered

    def load_game(self, game_id: str, socketio=None) -> BaseGame:
        """
        Load and instantiate a game by ID.

        Args:
            game_id: Game identifier from manifest
            socketio: Flask-SocketIO instance to pass to game

        Returns:
            Instantiated game object

        Raises:
            ValueError: If game not found or cannot be loaded
        """
        if game_id not in self.games:
            raise ValueError(f"Game '{game_id}' not found. Available: {list(self.games.keys())}")

        manifest = self.games[game_id]
        game_path = manifest['_path']

        # Parse entry point (e.g., "backend.game:ShapeSmashGame")
        entry_point = manifest['backend']['entry_point']
        if ':' not in entry_point:
            raise ValueError(f"Invalid entry point format: {entry_point}. Expected 'module:Class'")

        module_path, class_name = entry_point.split(':', 1)

        # Dynamically import the module
        try:
            # Load module from file path
            backend_dir = game_path / "backend"
            module_file = backend_dir / f"{module_path.split('.')[-1]}.py"

            if not module_file.exists():
                raise ValueError(f"Module file not found: {module_file}")

            spec = importlib.util.spec_from_file_location(module_path, module_file)
            if spec is None or spec.loader is None:
                raise ValueError(f"Could not load module spec for {module_file}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_path] = module
            spec.loader.exec_module(module)

            # Get the game class
            if not hasattr(module, class_name):
                raise ValueError(f"Class '{class_name}' not found in module {module_path}")

            game_class = getattr(module, class_name)

            # Instantiate with socketio
            game_instance = game_class(socketio=socketio)

            # Attach manifest metadata
            game_instance._manifest = manifest

            logger.info(f"Loaded game: {manifest['name']}")
            return game_instance

        except Exception as e:
            logger.error(f"Error loading game '{game_id}': {e}")
            raise ValueError(f"Failed to load game '{game_id}': {e}")

    def get_frontend_config(self, game_id: str) -> Dict[str, Any]:
        """
        Get frontend configuration for a game.

        Args:
            game_id: Game identifier

        Returns:
            Frontend configuration dictionary

        Raises:
            ValueError: If game not found
        """
        if game_id not in self.games:
            raise ValueError(f"Game '{game_id}' not found")

        manifest = self.games[game_id]
        return {
            'id': manifest['id'],
            'name': manifest['name'],
            'component': manifest['frontend']['component'],
            'entryPoint': manifest['frontend']['entry_point'],
            'assets': manifest['frontend'].get('assets', []),
            'config': manifest.get('config', {})
        }

    def get_manifest(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get the full manifest for a game"""
        return self.games.get(game_id)

    def list_games(self) -> List[str]:
        """Get list of all available game IDs"""
        return list(self.games.keys())
