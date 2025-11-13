"""
Shape Smash - Twitch Chat Interactive Game

A fun mini-game where stream viewers can spawn shapes using chat commands.
Shapes fall with gravity, bounce, and slow down due to friction.
"""
import pygame
import random
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

from shapes import Square, Circle, Triangle, COLORS
import twitch_bot

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
MAX_SHAPES = 50  # Limit to prevent lag


class Game:
    """Main game class handling rendering and physics"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Shape Smash - Twitch Chat Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 36)
        self.shapes = []
        self.running = True

        # Clear button configuration (top-right corner)
        self.clear_button_size = 30
        self.clear_button_rect = pygame.Rect(
            SCREEN_WIDTH - self.clear_button_size - 10,  # 10px from right edge
            10,  # 10px from top
            self.clear_button_size,
            self.clear_button_size
        )
        self.clear_button_hovered = False

    def add_shape(self, shape_type, username):
        """Add a new shape to the game"""
        color = random.choice(list(COLORS.values()))
        spawn_x = SCREEN_WIDTH // 2 - 20
        spawn_y = 50  # Spawn near top

        if shape_type == 'square':
            self.shapes.append(Square(spawn_x, spawn_y, color, username))
        elif shape_type == 'circle':
            self.shapes.append(Circle(spawn_x, spawn_y, color, username))
        elif shape_type == 'triangle':
            self.shapes.append(Triangle(spawn_x, spawn_y, color, username))

        # Limit number of shapes to prevent lag
        if len(self.shapes) > MAX_SHAPES:
            self.shapes.pop(0)

    def clear_shapes(self):
        """Clear all shapes from the screen"""
        self.shapes.clear()
        print("All shapes cleared!")

    def update(self):
        """Update all shapes and handle collisions"""
        # Update all shapes
        for shape in self.shapes:
            shape.update()

        # Check collisions between all pairs of shapes
        # Use nested loop but avoid checking same pair twice
        for i in range(len(self.shapes)):
            for j in range(i + 1, len(self.shapes)):
                shape1 = self.shapes[i]
                shape2 = self.shapes[j]
                if shape1.check_collision(shape2):
                    shape1.resolve_collision(shape2)

    def draw(self):
        """Draw all shapes"""
        self.screen.fill((30, 30, 30))  # Dark gray background

        # Draw title
        title = self.title_font.render("Shape Smash!", True, COLORS['white'])
        self.screen.blit(title, (SCREEN_WIDTH//2 - 100, 10))

        # Draw clear button (top-right corner)
        button_color = (200, 50, 50) if self.clear_button_hovered else (150, 50, 50)
        pygame.draw.rect(self.screen, button_color, self.clear_button_rect, border_radius=5)
        # Draw X symbol in the button
        pygame.draw.line(self.screen, COLORS['white'],
                        (self.clear_button_rect.left + 8, self.clear_button_rect.top + 8),
                        (self.clear_button_rect.right - 8, self.clear_button_rect.bottom - 8), 3)
        pygame.draw.line(self.screen, COLORS['white'],
                        (self.clear_button_rect.right - 8, self.clear_button_rect.top + 8),
                        (self.clear_button_rect.left + 8, self.clear_button_rect.bottom - 8), 3)

        # Draw instructions
        instructions = self.font.render("Commands: !square, !circle, !triangle, !boost", True, COLORS['white'])
        self.screen.blit(instructions, (20, SCREEN_HEIGHT - 30))

        # Draw shape count
        count_text = self.font.render(f"Shapes: {len(self.shapes)}", True, COLORS['white'])
        self.screen.blit(count_text, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30))

        # Draw all shapes
        for shape in self.shapes:
            shape.draw(self.screen, self.font)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            # Get mouse position for button hover effect
            mouse_pos = pygame.mouse.get_pos()
            self.clear_button_hovered = self.clear_button_rect.collidepoint(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.clear_button_rect.collidepoint(event.pos):
                            self.clear_shapes()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def run_bot(game):
    """Run the Twitch bot in a separate thread"""
    twitch_bot.main(game)


if __name__ == '__main__':
    # Create game instance
    game = Game()

    # Start Twitch bot in separate thread
    bot_thread = threading.Thread(target=run_bot, args=(game,), daemon=True)
    bot_thread.start()

    print("Starting Shape Smash game...")
    print("Chat commands available: !square, !circle, !triangle, !boost")

    # Run game (this blocks until window is closed)
    game.run()
