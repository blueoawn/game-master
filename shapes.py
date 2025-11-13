"""
Shape classes for the Shape Smash game.
Contains base Shape class and all shape implementations.
"""
import pygame
import random

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.5
FRICTION = 0.98
BOUNCE_DAMPING = 0.7

# Colors
COLORS = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128),
    'orange': (255, 165, 0),
    'cyan': (0, 255, 255),
    'pink': (255, 192, 203),
    'white': (255, 255, 255)
}


class Shape:
    """Base class for all shapes in the game"""
    def __init__(self, x, y, color, username):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)  # Random horizontal velocity
        self.vy = random.uniform(-10, -5)  # Initial upward velocity
        self.color = color
        self.username = username
        self.size = random.randint(20, 40)
        # Mass is proportional to size (larger shapes are heavier)
        # Using size squared to make mass difference more significant
        self.mass = (self.size / 30.0) ** 2  # Normalized around size 30

    def update(self):
        """Update shape physics"""
        # Apply gravity
        self.vy += GRAVITY

        # Apply friction to horizontal movement
        self.vx *= FRICTION

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Bottom collision
        if self.y + self.size > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.size
            self.vy = -self.vy * BOUNCE_DAMPING
            self.vx *= FRICTION

        # Top collision
        if self.y < 0:
            self.y = 0
            self.vy = -self.vy * BOUNCE_DAMPING

        # Left wall collision
        if self.x < 0:
            self.x = 0
            self.vx = -self.vx * BOUNCE_DAMPING

        # Right wall collision
        if self.x + self.size > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.size
            self.vx = -self.vx * BOUNCE_DAMPING

        # Stop if velocity is very low
        if abs(self.vx) < 0.1:
            self.vx = 0
        if abs(self.vy) < 0.1 and self.y + self.size >= SCREEN_HEIGHT - 1:
            self.vy = 0

    def is_static(self):
        """Check if shape has stopped moving"""
        return abs(self.vx) < 0.1 and abs(self.vy) < 0.1

    def get_center(self):
        """Get the center point of the shape"""
        return (self.x + self.size / 2, self.y + self.size / 2)

    def check_collision(self, other):
        """Check if this shape is colliding with another shape"""
        # Get centers
        x1, y1 = self.get_center()
        x2, y2 = other.get_center()

        # Calculate distance between centers
        dx = x2 - x1
        dy = y2 - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Check if distance is less than sum of radii (treating shapes as circles)
        min_distance = (self.size + other.size) / 2
        return distance < min_distance

    def resolve_collision(self, other):
        """Resolve collision using elastic collision physics"""
        # Get centers
        x1, y1 = self.get_center()
        x2, y2 = other.get_center()

        # Calculate distance and direction
        dx = x2 - x1
        dy = y2 - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Avoid division by zero
        if distance == 0:
            distance = 0.01

        # Normalize direction vector
        nx = dx / distance
        ny = dy / distance

        # Separate overlapping shapes
        overlap = (self.size + other.size) / 2 - distance
        if overlap > 0:
            # Move shapes apart proportionally to their masses
            mass_ratio = self.mass / (self.mass + other.mass)
            self.x -= nx * overlap * (1 - mass_ratio)
            self.y -= ny * overlap * (1 - mass_ratio)
            other.x += nx * overlap * mass_ratio
            other.y += ny * overlap * mass_ratio

        # Calculate relative velocity
        dvx = other.vx - self.vx
        dvy = other.vy - self.vy

        # Calculate relative velocity in collision normal direction
        dvn = dvx * nx + dvy * ny

        # Don't resolve if velocities are separating
        if dvn > 0:
            return

        # Calculate impulse (using coefficient of restitution = 0.8 for bouncy collisions)
        restitution = 0.8
        impulse = -(1 + restitution) * dvn / (1 / self.mass + 1 / other.mass)

        # Apply impulse to velocities
        self.vx -= impulse * nx / self.mass
        self.vy -= impulse * ny / self.mass
        other.vx += impulse * nx / other.mass
        other.vy += impulse * ny / other.mass

    def draw(self, screen, font):
        """Draw method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement draw method")


class Square(Shape):
    """Square shape"""
    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.size, self.size))
        # Draw username above shape
        text = font.render(self.username, True, COLORS['white'])
        screen.blit(text, (int(self.x), int(self.y) - 20))


class Circle(Shape):
    """Circle shape"""
    def draw(self, screen, font):
        pygame.draw.circle(screen, self.color, (int(self.x + self.size/2), int(self.y + self.size/2)), self.size//2)
        # Draw username above shape
        text = font.render(self.username, True, COLORS['white'])
        screen.blit(text, (int(self.x), int(self.y) - 20))


class Triangle(Shape):
    """Triangle shape"""
    def draw(self, screen, font):
        points = [
            (int(self.x + self.size/2), int(self.y)),
            (int(self.x), int(self.y + self.size)),
            (int(self.x + self.size), int(self.y + self.size))
        ]
        pygame.draw.polygon(screen, self.color, points)
        # Draw username above shape
        text = font.render(self.username, True, COLORS['white'])
        screen.blit(text, (int(self.x), int(self.y) - 20))
