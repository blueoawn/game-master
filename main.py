"""
Multi-Game Twitch Stream Application
Main entry point that manages game cycling and Twitch bot integration.
"""
import pygame
import threading
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load .env from git root (parent of chat-games folder)
    git_root = Path(__file__).parent.parent
    env_path = git_root / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    load_dotenv = None

from game_manager import GameManager
from games.shape_smash import ShapeSmashGame
from assets.physics import SCREEN_WIDTH, SCREEN_HEIGHT
import twitch_bot

# Game constants
FPS = 60


def run_bot(game_manager):
    """Run the Twitch bot in a separate thread"""
    twitch_bot.main(game_manager)


def main():
    """Main entry point for the application"""
    # Initialize Pygame
    pygame.init()

    # Create display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Twitch Chat Games")

    clock = pygame.time.Clock()

    # Create game manager
    game_manager = GameManager(screen)

    # Register games
    shape_smash = ShapeSmashGame(
        game_manager.get_font(),
        game_manager.get_title_font()
    )
    game_manager.register_game(shape_smash)

    # TODO: Register more games here as you create them
    # example_game = ExampleGame(game_manager.get_font(), game_manager.get_title_font())
    # game_manager.register_game(example_game)

    # Initialize the first game
    game_manager.get_active_game().reset()

    # Start Twitch bot in separate thread
    bot_thread = threading.Thread(
        target=run_bot,
        args=(game_manager,),
        daemon=True
    )
    bot_thread.start()

    print("=" * 50)
    print("Twitch Chat Games Started!")
    print("=" * 50)
    print(f"Active Game: {game_manager.get_active_game().get_title()}")
    print(f"Registered Games: {len(game_manager.games)}")
    for i, game in enumerate(game_manager.games):
        print(f"  {i+1}. {game.get_title()}")
    print("\nModerator Commands:")
    print("  !nextgame - Switch to next game")
    print("\nGame-specific commands will appear in chat!")
    print("=" * 50)

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Let the active game handle mouse clicks
                    active_game = game_manager.get_active_game()
                    if hasattr(active_game, 'handle_mouse_click'):
                        active_game.handle_mouse_click(event.pos)

        # Update game
        game_manager.update()

        # Draw game
        game_manager.draw()

        # Update display
        pygame.display.flip()

        # Maintain FPS
        clock.tick(FPS)

    # Cleanup
    pygame.quit()
    print("\nShutting down...")


if __name__ == '__main__':
    main()
