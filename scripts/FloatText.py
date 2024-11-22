import pygame
from scripts.entities import PhysicsEntity, Player #Should I make this an entity so i have its coords? But then it'll collide with shit

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), duration=1.0):
        self.x = x  # Initial x position
        self.y = y  # Initial y position
        self.text = text  # The text to display
        self.font = pygame.font.Font(None, 15)  # Font for rendering
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
        """Render the text with a black outline."""
        text_surface = self.font.render(self.text, True, self.color)
        outline_surface = self.font.render(self.text, True, (0, 0, 0))  # Black outline
        
        # Positions for the outline
        outline_positions = [
            (-1, -1), (0, -1), (1, -1),  # Top-left, Top, Top-right
            (-1, 0),          (1, 0),   # Left, Right
            (-1, 1), (0, 1), (1, 1)    # Bottom-left, Bottom, Bottom-right
        ]
        
        # Draw the outline
        for offset in outline_positions:
            screen.blit(outline_surface, (self.x + offset[0], self.y + offset[1]))
        
        # Draw the main text
        screen.blit(text_surface, (self.x, self.y))
