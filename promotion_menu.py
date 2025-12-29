# # promotion_menu.py
# when a pawn reaches final row, it opens a promotion menu so user may select the required piece to create.
import pygame

MENU_BG = (245, 245, 245)
MENU_BORDER = (100, 100, 100)
MENU_HOVER = (200, 220, 255)


# Handles the promotion piece selection menu
class PromotionMenu:
    def __init__(self, color, WIDTH):
        self.color = color  # 'w' or 'b'
        self.pieces = ['Q', 'R', 'B', 'N']
        self.piece_size = 80
        self.padding = 10
        self.menu_width = len(self.pieces) * (self.piece_size + self.padding) + self.padding
        self.menu_height = self.piece_size + 2 * self.padding
        self.menu_x = (WIDTH - self.menu_width) // 2
        self.menu_y = 50
        self.selected_piece = None

    # Draw the promotion menu
    def draw(self, screen, IMAGES):
        # Draw title
        font = pygame.font.SysFont('Arial', 20, True)
        title = font.render("  Choose promotion piece:", True, pygame.Color('Black'))
        text_location = pygame.Rect(self.menu_x, self.menu_y - 30, self.menu_width, self.menu_height)
        screen.fill(pygame.Color('White'), text_location)
        screen.blit(title, text_location)

        # draw rectangle
        pygame.draw.rect(screen, MENU_BG, (self.menu_x, self.menu_y, self.menu_width, self.menu_height))
        pygame.draw.rect(screen, MENU_BORDER,(self.menu_x, self.menu_y, self.menu_width, self.menu_height), 3)

        # Get mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()

        # Draw each piece option
        for i, piece in enumerate(self.pieces):
            x = self.menu_x + self.padding + i * (self.piece_size + self.padding)
            y = self.menu_y + self.padding

            # Check if mouse is hovering
            rect = pygame.Rect(x, y, self.piece_size, self.piece_size)
            if rect.collidepoint(mouse_pos):
                # Draw hover highlight
                pygame.draw.rect(screen, MENU_HOVER, rect)

            # Draw border
            pygame.draw.rect(screen, MENU_BORDER, rect, 2)

            # Draw piece image (centered)
            piece_code = self.color + piece
            piece_img = IMAGES[piece_code]
            img_x = x + (self.piece_size - piece_img.get_width()) // 2
            img_y = y + (self.piece_size - piece_img.get_height()) // 2
            screen.blit(piece_img, (img_x, img_y))

    # Check if a piece was clicked and return it
    def handle_click(self, pos):
        for i, piece in enumerate(self.pieces):
            x = self.menu_x + self.padding + i * (self.piece_size + self.padding)
            y = self.menu_y + self.padding
            rect = pygame.Rect(x, y, self.piece_size, self.piece_size)

            if rect.collidepoint(pos):
                return piece
        return None
