import pygame
from scripts.entities import PhysicsEntity, Player #Should I make this an entity so i have its coords? But then it'll collide with shit

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), duration=1.0):
        self.x = x  # Initial x position
        self.y = y  # Initial y position
        self.text = text  # The text to display
        self.font = pygame.font.Font(None, 12)  # Font for rendering
        self.color = color  # Color of the text
        self.duration = duration  # How long the text will last (seconds)
        self.start_time = pygame.time.get_ticks()  # Record the spawn time

    def update(self):
        """Update the position of the text."""
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        #self.y -= 50 * (1 / 60)  # Move up (50 pixels per second)
        if elapsed_time > self.duration:
            return False  # Signal that this text should be removed
        return True

    def render(self, screen):
        """Render the text."""
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.x, self.y))
