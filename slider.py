# # slider.py
import pygame

MENU_BG = (245, 245, 245)
MENU_BORDER = (100, 100, 100)
MENU_HOVER = (200, 220, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)


# Slider for selecting AI difficulty level
class Slider:

    def __init__(self, x, y, width, height, min_val=0, max_val=20, initial_val=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

        # Parameters
        self.track_height = 8
        self.handle_radius = 12
        self.track_y = y + height // 2

        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 20, True)
        self.value_font = pygame.font.SysFont('Arial', 24, True)
        self.desc_font = pygame.font.SysFont('Arial', 18)

    # Return description based on skill level
    def get_difficulty_description(self):
        if self.value <= 5:
            return "Beginner"
        elif self.value <= 10:
            return "Intermediate"
        elif self.value <= 15:
            return "Advanced"
        else:
            return "Expert"

    # Calculate handle x position based on value
    def get_handle_x(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(ratio * self.rect.width)

    # Set value based on x position
    def set_value_from_x(self, x):
        ratio = (x - self.rect.x) / self.rect.width
        ratio = max(0, min(1, ratio))  # Clamp between 0 and 1
        self.value = int(self.min_val + ratio * (self.max_val - self.min_val))

    # Draw the slider
    def draw(self, screen):
        # Draw title
        title = self.title_font.render("AI Difficulty Level:", True, pygame.Color('Black'))
        screen.blit(title, (self.rect.x, self.rect.y - 4))

        # Draw track
        track_rect = pygame.Rect(self.rect.x, self.track_y - self.track_height // 2,
                    self.rect.width, self.track_height)
        pygame.draw.rect(screen, (200, 200, 200), track_rect, border_radius=4)

        # Draw filled portion
        handle_x = self.get_handle_x()
        filled_width = handle_x - self.rect.x
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.track_y - self.track_height // 2,
                        filled_width, self.track_height)
            pygame.draw.rect(screen, BUTTON_COLOR, filled_rect, border_radius=4)

        # Draw handle
        handle_color = BUTTON_HOVER if self.dragging else BUTTON_COLOR
        pygame.draw.circle(screen, handle_color, (handle_x, self.track_y), self.handle_radius)
        pygame.draw.circle(screen, MENU_BORDER, (handle_x, self.track_y), self.handle_radius, 3)

        # Draw value and description
        value_text = self.value_font.render(f"Level {self.value} ({self.get_difficulty_description()})", True, pygame.Color('Black'))

        value_x = self.rect.x + self.rect.width // 2 - value_text.get_width() // 2

        screen.blit(value_text, (value_x, self.track_y + 25))

        # Draw tick marks for reference
        for i in range(self.min_val, self.max_val + 1, 5):
            ratio = (i - self.min_val) / (self.max_val - self.min_val)
            tick_x = self.rect.x + int(ratio * self.rect.width)
            pygame.draw.line(screen, (150, 150, 150),
                             (tick_x, self.track_y + self.track_height // 2 + 2),
                             (tick_x, self.track_y + self.track_height // 2 + 8), 2)

            # Draw number labels
            label_font = pygame.font.SysFont('Arial', 12)
            label = label_font.render(str(i), True, pygame.Color('Gray'))
            screen.blit(label, (tick_x - label.get_width() // 2, self.track_y + 12))

    # Handle mouse events for slider
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            handle_x = self.get_handle_x()

            # Check if clicked on handle
            distance = ((mouse_x - handle_x) ** 2 + (mouse_y - self.track_y) ** 2) ** 0.5
            if distance <= self.handle_radius:
                self.dragging = True
                return True

            # Check if clicked on track
            if self.rect.collidepoint(mouse_x, mouse_y):
                self.set_value_from_x(mouse_x)
                self.dragging = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.set_value_from_x(mouse_x)
                return True

        return False
