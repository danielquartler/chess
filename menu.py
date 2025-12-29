# # menu.py
import pygame
from slider import Slider

# Constants
MAX_FPS = 15

# Colors
MENU_BG = (245, 245, 245)
MENU_BORDER = (100, 100, 100)
MENU_HOVER = (200, 220, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)


# Show main menu and return game mode and player color
def show_menu(screen, WIDTH):
    clock = pygame.time.Clock()

    # Create buttons
    button_width = 300
    button_height = 60
    button_x = (WIDTH - button_width) // 2

    btn_vs_friend = Button(button_x, 200, button_width, button_height, "Play vs Friend")
    btn_vs_ai = Button(button_x, 300, button_width, button_height, "Play vs AI")

    # Color selection buttons (initially hidden)
    btn_white = Button(button_x, 520, 140, 50, "White", 20)
    btn_black = Button(button_x + 160, 520, 140, 50, "Black", 20)

    # Difficulty slider
    slider_width = 350
    slider_x = (WIDTH - slider_width) // 2
    difficulty_slider = Slider(slider_x, 380, slider_width, 80, min_val=0, max_val=20, initial_val=10)

    # init state
    AI_mode = False  # True: play vs 'ai'  ;  False: play vs 'friend'

    # enable menu (waits for user selection)
    while True:
        screen.fill(pygame.Color('white'))

        # Draw title
        title_font = pygame.font.SysFont('Arial', 48, True)
        title = title_font.render("Chess Game", True, pygame.Color('Black'))
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title, title_rect)

        # Draw mode buttons
        btn_vs_friend.draw(screen)
        btn_vs_ai.draw(screen)

        # If AI mode selected, show: difficulty + color selection
        if AI_mode:
            # Draw difficulty slider
            difficulty_slider.draw(screen)

            # Draw color selection instruction
            instruction_font = pygame.font.SysFont('Arial', 24)
            instruction = instruction_font.render("Choose your color:", True, pygame.Color('Black'))
            inst_rect = instruction.get_rect(center=(WIDTH // 2, 495))
            screen.blit(instruction, inst_rect)

            btn_white.draw(screen)
            btn_black.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None

            # Handle button events
            if btn_vs_friend.handle_event(event):
                return 'friend', None, None

            if btn_vs_ai.handle_event(event):
                AI_mode = True

            if AI_mode:
                # Handle slider events
                difficulty_slider.handle_event(event)
                if btn_white.handle_event(event):
                    return 'ai', 'white', difficulty_slider.value
                if btn_black.handle_event(event):
                    return 'ai', 'black', difficulty_slider.value

            # Update hover states
            btn_vs_friend.handle_event(event)
            btn_vs_ai.handle_event(event)
            if AI_mode:
                btn_white.handle_event(event)
                btn_black.handle_event(event)

        pygame.display.flip()
        clock.tick(MAX_FPS)


# button class
class Button:
    def __init__(self, x, y, width, height, text, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont('Arial', font_size, True)
        self.hovered = False

    def draw(self, screen):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, MENU_BORDER, self.rect, 3, border_radius=10)

        text_surf = self.font.render(self.text, True, pygame.Color('White'))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
