"""
Base game class that all games must inherit from.
Defines the interface for the game manager and bot integration.
"""
from abc import ABC, abstractmethod


class BaseGame(ABC):
    """Abstract base class for all games"""

    def __init__(self):
        """Initialize the game"""
        pass

    @abstractmethod
    def get_title(self) -> str:
        """
        Return the game's display title.

        Returns:
            str: The name of the game to display
        """
        pass

    @abstractmethod
    def get_commands(self) -> dict:
        """
        Return a dictionary of chat commands for this game.

        Returns:
            dict: Dictionary mapping command names (without !) to callback functions
                  Example: {'square': self.spawn_square, 'boost': self.boost_shapes}
        """
        pass

    @abstractmethod
    def update(self):
        """
        Update game logic for one frame.
        Called once per frame by the game manager.
        """
        pass

    @abstractmethod
    def draw(self, screen):
        """
        Draw the game to the screen.

        Args:
            screen: Pygame screen surface to draw on
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the game state to initial conditions.
        Called when cycling to this game or when game restarts.
        Player stats should be preserved elsewhere.
        """
        pass

    def finish(self):
        """
        Signal that the game has ended and should transition to next game.
        Optional method - games can call this to self-initiate transitions.

        Returns:
            bool: True if game is finished, False otherwise
        """
        return False

    def handle_collision_detection(self):
        """
        Optional collision detection handling.
        Games with physics can override this.
        """
        pass
