"""
Game Manager - Handles game cycling and coordination between games and the bot.
"""
import pygame
from games.base_game import BaseGame


class GameManager:
    """Manages multiple games, handles cycling, and coordinates with the bot"""

    def __init__(self, screen):
        """
        Initialize the game manager.

        Args:
            screen: Pygame screen surface shared by all games
        """
        self.screen = screen
        self.games = []  # List of registered game instances
        self.current_game_index = 0
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)

    def register_game(self, game: BaseGame):
        """
        Register a new game with the manager.

        Args:
            game: Instance of a game class inheriting from BaseGame
        """
        if not isinstance(game, BaseGame):
            raise TypeError(f"Game must inherit from BaseGame, got {type(game)}")
        self.games.append(game)
        print(f"Registered game: {game.get_title()}")

    def get_active_game(self) -> BaseGame:
        """
        Get the currently active game.

        Returns:
            BaseGame: The active game instance
        """
        if not self.games:
            raise RuntimeError("No games registered with GameManager")
        return self.games[self.current_game_index]

    def next_game(self):
        """
        Cycle to the next game in the list.
        Resets the new game's state.
        """
        if len(self.games) <= 1:
            print("Only one game registered, cannot cycle")
            return

        # Move to next game
        self.current_game_index = (self.current_game_index + 1) % len(self.games)

        # Reset the new game
        new_game = self.get_active_game()
        new_game.reset()

        print(f"Switched to game: {new_game.get_title()}")

    def update(self):
        """
        Update the active game and check if it has finished.
        """
        active_game = self.get_active_game()
        active_game.update()

        # Check if game has signaled it's finished (for future auto-cycling)
        if active_game.finish():
            print(f"{active_game.get_title()} has finished!")
            self.next_game()

    def draw(self):
        """
        Draw the active game to the screen.
        """
        active_game = self.get_active_game()
        active_game.draw(self.screen)

    def get_active_commands(self) -> dict:
        """
        Get the command dictionary from the active game.

        Returns:
            dict: Command name -> callback function mapping
        """
        return self.get_active_game().get_commands()

    def get_font(self):
        """Get the standard font for games to use"""
        return self.font

    def get_title_font(self):
        """Get the title font for games to use"""
        return self.title_font
