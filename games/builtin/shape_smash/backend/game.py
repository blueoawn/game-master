"""
Shape Smash Game - Backend
Handles chat commands and state management for the shape spawning game.
"""
import sys
from pathlib import Path
import random
import uuid

# Add backend to path for imports
backend_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from base_game import BaseGame

# Shape types and colors
SHAPE_TYPES = ['square', 'circle', 'triangle']
COLORS = [
    '#FF6B6B',  # Red
    '#4ECDC4',  # Cyan
    '#45B7D1',  # Blue
    '#FFA07A',  # Light Salmon
    '#98D8C8',  # Mint
    '#F7DC6F',  # Yellow
    '#BB8FCE',  # Purple
    '#85C1E2',  # Sky Blue
    '#F8B739',  # Orange
    '#52C77D',  # Green
]

MAX_SHAPES = 50


class ShapeSmashGame(BaseGame):
    """Shape Smash - Physics-based shape spawning game"""

    def __init__(self, socketio=None):
        super().__init__(socketio)
        self.shapes = []
        self.max_shapes = MAX_SHAPES

    def get_title(self) -> str:
        """Return game title"""
        return "Shape Smash"

    def get_game_id(self) -> str:
        """Return game identifier"""
        return "shape_smash"

    def get_commands(self) -> dict:
        """Return available chat commands"""
        return {
            'square': self.spawn_square,
            'circle': self.spawn_circle,
            'triangle': self.spawn_triangle,
            'boost': self.boost_shapes,
            'clear': self.clear_shapes,
            'explode': self.explode_shapes
        }

    def get_initial_state(self) -> dict:
        """Return initial game state"""
        return {
            'shapes': [],
            'shape_count': 0
        }

    def get_frontend_config(self) -> dict:
        """Return frontend configuration"""
        return {
            'component': 'ShapeSmash',
            'canvas_width': 1920,
            'canvas_height': 1080,
            'max_shapes': MAX_SHAPES
        }

    # === Command Handlers ===

    def spawn_square(self, message):
        """Spawn a square shape"""
        self._add_shape('square', message.chatter.name)

    def spawn_circle(self, message):
        """Spawn a circle shape"""
        self._add_shape('circle', message.chatter.name)

    def spawn_triangle(self, message):
        """Spawn a triangle shape"""
        self._add_shape('triangle', message.chatter.name)

    def boost_shapes(self, message):
        """Give all shapes an upward boost"""
        # Emit boost event to frontend
        self.emit_state({
            'event': 'boost',
            'username': message.chatter.name
        })
        print(f"{message.chatter.name} boosted all shapes!")

    def clear_shapes(self, message):
        """Clear all shapes (broadcaster/mod only)"""
        if message.chatter.is_mod or message.chatter.is_broadcaster:
            self.shapes = []
            self.update_state({
                'shapes': [],
                'shape_count': 0,
                'event': 'clear',
                'username': message.chatter.name
            })
            print(f"{message.chatter.name} cleared all shapes!")

    def explode_shapes(self, message):
        """Make shapes explode outward from center"""
        self.emit_state({
            'event': 'explode',
            'username': message.chatter.name
        })
        print(f"{message.chatter.name} exploded all shapes!")

    # === Helper Methods ===

    def _add_shape(self, shape_type: str, username: str):
        """Internal method to add a shape"""
        # Create shape data
        shape_data = {
            'id': str(uuid.uuid4()),
            'type': shape_type,
            'x': 960,  # Center of 1920px screen
            'y': 50,
            'vx': 0,
            'vy': 0,
            'color': random.choice(COLORS),
            'username': username
        }

        self.shapes.append(shape_data)

        # Limit number of shapes
        if len(self.shapes) > self.max_shapes:
            removed = self.shapes.pop(0)
            print(f"Removed oldest shape (max {self.max_shapes} reached)")

        # Emit state update
        self.update_state({
            'shapes': self.shapes,
            'shape_count': len(self.shapes),
            'shape_added': shape_data  # Signal for animation
        })

    def reset(self):
        """Reset game state"""
        self.shapes = []
        super().reset()
