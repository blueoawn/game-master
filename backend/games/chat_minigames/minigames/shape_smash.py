"""
Shape Smash Minigame
Interactive physics sandbox where viewers spawn shapes
"""
import random
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class ShapeSmashMinigame:
    """
    Shape Smash minigame - Physics-based shape spawning
    """

    # Color palette for shapes
    COLORS = [
        '#FF6B6B',  # Red
        '#4ECDC4',  # Teal
        '#45B7D1',  # Blue
        '#FFA07A',  # Light Salmon
        '#98D8C8',  # Mint
        '#F7DC6F',  # Yellow
        '#BB8FCE',  # Purple
        '#85C1E2',  # Sky Blue
        '#F8B195',  # Peach
        '#C06C84',  # Mauve
    ]

    def __init__(self, parent_game):
        """
        Initialize Shape Smash minigame

        Args:
            parent_game: Reference to ChatMinigamesGame orchestrator
        """
        self.parent = parent_game
        self.shapes = []
        self.shape_id_counter = 0

    # === METADATA ===

    def get_minigame_id(self) -> str:
        """Return minigame identifier"""
        return "shape_smash"

    # === COMMANDS ===

    def get_commands(self) -> Dict[str, Callable]:
        """Return command handlers for this minigame"""
        return {
            'square': self.spawn_square,
            'circle': self.spawn_circle,
            'triangle': self.spawn_triangle,
            'boost': self.boost_shapes,
            'explode': self.explode_shapes,
            'clear': self.clear_shapes
        }

    # === STATE MANAGEMENT ===

    def get_initial_state(self) -> Dict[str, Any]:
        """Return initial minigame state"""
        return {
            'shapes': [],
            'shape_count': 0
        }

    # === SHAPE SPAWNING ===

    def spawn_square(self, message):
        """Spawn a square for the user"""
        shape = self._create_shape('square', message.chatter.name)
        self._emit_shape_added(shape)

    def spawn_circle(self, message):
        """Spawn a circle for the user"""
        shape = self._create_shape('circle', message.chatter.name)
        self._emit_shape_added(shape)

    def spawn_triangle(self, message):
        """Spawn a triangle for the user"""
        shape = self._create_shape('triangle', message.chatter.name)
        self._emit_shape_added(shape)

    def _create_shape(self, shape_type: str, username: str) -> Dict[str, Any]:
        """
        Create a new shape with random position and properties

        Args:
            shape_type: Type of shape ('square', 'circle', 'triangle')
            username: Username of the spawner

        Returns:
            Shape data dictionary
        """
        # Generate unique ID
        self.shape_id_counter += 1
        shape_id = f"shape_{self.shape_id_counter}"

        # Random spawn position (top half of screen)
        x = random.randint(200, 1720)  # Leave margins
        y = random.randint(150, 400)   # Top half

        # Random color
        color = random.choice(self.COLORS)

        # Random initial velocity
        vx = random.uniform(-50, 50)
        vy = random.uniform(-20, 20)

        shape = {
            'id': shape_id,
            'type': shape_type,
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'color': color,
            'username': username
        }

        # Add to shapes list
        self.shapes.append(shape)

        logger.info(f"Created {shape_type} for {username} at ({x}, {y})")

        return shape

    def _emit_shape_added(self, shape: Dict[str, Any]):
        """Emit a shape_added event to frontend"""
        self.parent.emit_state({
            'shape_added': shape,
            'shape_count': len(self.shapes)
        })

    # === SHAPE EVENTS ===

    def boost_shapes(self, message):
        """Boost all shapes upward"""
        username = message.chatter.name

        # Use emit_event() for transient events (won't persist in game_state)
        self.parent.emit_event('boost', {'username': username})

        logger.info(f"{username} boosted all shapes")

    def explode_shapes(self, message):
        """Explode shapes from center"""
        username = message.chatter.name

        # Use emit_event() for transient events (won't persist in game_state)
        self.parent.emit_event('explode', {'username': username})

        logger.info(f"{username} exploded shapes")

    def clear_shapes(self, message):
        """Clear all shapes"""
        username = message.chatter.name

        # Clear local state
        self.shapes = []
        self.shape_id_counter = 0

        # Emit transient event for visual effect
        self.parent.emit_event('clear', {'username': username})

        # Emit persistent state update for shape count
        self.parent.emit_state({'shape_count': 0})

        logger.info(f"{username} cleared all shapes")

    # === LIFECYCLE ===

    def on_activate(self):
        """Called when this minigame becomes active"""
        # Reset state when activated
        self.shapes = []
        self.shape_id_counter = 0

        # Send initial state
        self.parent.emit_state(self.get_initial_state())

        logger.info("Shape Smash activated")

    def on_deactivate(self):
        """Called when switching away from this minigame"""
        logger.info("Shape Smash deactivated")
