"""
Shape Smash Game - Twitch chat interactive physics sandbox.
Players spawn shapes that fall, bounce, and collide.
"""
import pygame
import random
from games.base_game import BaseGame
from assets.shapes import Square, Circle, Triangle
from assets.colors import COLORS
from assets.physics import SCREEN_WIDTH, SCREEN_HEIGHT

# Shape Smash specific constants
MAX_SHAPES = 50  # Limit to prevent lag


class ShapeSmashGame(BaseGame):
    """Shape Smash - Physics-based shape spawning game"""

    def __init__(self, font, title_font):
        """
        Initialize Shape Smash game.

        Args:
            font: Pygame font for regular text
            title_font: Pygame font for title text
        """
        super().__init__()
        self.font = font
        self.title_font = title_font
        self.shapes = []

        # Clear button configuration (top-right corner)
        self.clear_button_size = 30
        self.clear_button_rect = pygame.Rect(
            SCREEN_WIDTH - self.clear_button_size - 10,
            10,
            self.clear_button_size,
            self.clear_button_size
        )
        self.clear_button_hovered = False

    def get_title(self) -> str:
        """Return game title"""
        return "Shape Smash"

    def get_commands(self) -> dict:
        """Return available chat commands"""
        return {
            'square': self.spawn_square,
            'circle': self.spawn_circle,
            'triangle': self.spawn_triangle,
            'boost': self.boost_shapes,
            'clear': self.clear_shapes,
            #'spin': self.spin_shapes,
            'explode': self.explode_shapes
            #'gravity': self.toggle_gravity
        }

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
        for shape in self.shapes:
            shape.vy -= 15
        print(f"{message.chatter.name} boosted all shapes!")

    def clear_shapes(self, message):
        """Clear all shapes (broadcaster/mod only)"""
        if message.chatter.is_mod or message.chatter.is_broadcaster:
            self.shapes.clear()
            print(f"{message.chatter.name} cleared all shapes!")

    def spin_shapes(self, message):
        """Make all shapes spin in circles"""
       # Not currently implemented

    def explode_shapes(self, message):
        """Make shapes explode outward from center"""
        center_x, center_y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        for shape in self.shapes:
            dx = shape.x - center_x
            dy = shape.y - center_y
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                shape.vx = (dx / distance) * 100
                shape.vy = (dy / distance) * 100
        print(f"{message.chatter.name} exploded all shapes!")

    def toggle_gravity(self, message):
        """Toggle gravity (reverse it)"""
        # Not currently implemented

    def _add_shape(self, shape_type, username):
        """Internal method to add a shape"""
        color = random.choice(list(COLORS.values()))
        spawn_x = SCREEN_WIDTH // 2 - 20
        spawn_y = 50

        if shape_type == 'square':
            self.shapes.append(Square(spawn_x, spawn_y, color, username))
        elif shape_type == 'circle':
            self.shapes.append(Circle(spawn_x, spawn_y, color, username))
        elif shape_type == 'triangle':
            self.shapes.append(Triangle(spawn_x, spawn_y, color, username))

        # Limit number of shapes
        if len(self.shapes) > MAX_SHAPES:
            self.shapes.pop(0)

    def update(self):
        """Update all shapes and handle collisions"""
        # Update all shapes
        for shape in self.shapes:
            shape.update()

        # Check collisions between all pairs
        for i in range(len(self.shapes)):
            for j in range(i + 1, len(self.shapes)):
                shape1 = self.shapes[i]
                shape2 = self.shapes[j]
                if shape1.check_collision(shape2):
                    shape1.resolve_collision(shape2)

    def draw(self, screen):
        """Draw the game"""
        screen.fill((30, 30, 30))  # Dark gray background

        # Draw title
        title = self.title_font.render("Shape Smash!", True, COLORS['white'])
        screen.blit(title, (SCREEN_WIDTH // 2 - 100, 10))

        # Draw clear button
        mouse_pos = pygame.mouse.get_pos()
        self.clear_button_hovered = self.clear_button_rect.collidepoint(mouse_pos)
        button_color = (200, 50, 50) if self.clear_button_hovered else (150, 50, 50)
        pygame.draw.rect(screen, button_color, self.clear_button_rect, border_radius=5)

        # Draw X in button
        pygame.draw.line(screen, COLORS['white'],
                        (self.clear_button_rect.left + 8, self.clear_button_rect.top + 8),
                        (self.clear_button_rect.right - 8, self.clear_button_rect.bottom - 8), 3)
        pygame.draw.line(screen, COLORS['white'],
                        (self.clear_button_rect.right - 8, self.clear_button_rect.top + 8),
                        (self.clear_button_rect.left + 8, self.clear_button_rect.bottom - 8), 3)

        # Draw instructions
        instructions = self.font.render(
            "Commands: !square, !circle, !triangle, !boost, !spin, !explode, !gravity", # 
            True, COLORS['white']
        )
        screen.blit(instructions, (20, SCREEN_HEIGHT - 30))

        # Draw shape count
        count_text = self.font.render(f"Shapes: {len(self.shapes)}", True, COLORS['white'])
        screen.blit(count_text, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30))

        # Draw all shapes
        for shape in self.shapes:
            shape.draw(screen, self.font)

    def reset(self):
        """Reset game state"""
        self.shapes.clear()
        # Reset gravity to normal if it was changed
        from assets import physics
        if physics.GRAVITY < 0:
            physics.GRAVITY = -physics.GRAVITY

    def handle_mouse_click(self, pos):
        """Handle mouse click events (for clear button)"""
        if self.clear_button_rect.collidepoint(pos):
            self.shapes.clear()
            print("Shapes cleared via button!")
            return True
        return False
