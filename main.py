import pygame
import sys
from promotion_menu import PromotionMenu
from chess_board import ChessBoard, Move

# Constants
WIDTH, HEIGHT = 640, 640
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15

# Colors
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
SELECT = (246, 246, 130)

# Pieces images
IMAGES = {}
image_names = {
    'wP': 'white_pawn', 'wR': 'white_rock', 'wN': 'white_knight',
    'wB': 'white_bishop', 'wQ': 'white_queen', 'wK': 'white_king',
    'bP': 'black_pawn', 'bR': 'black_rock', 'bN': 'black_knight',
    'bB': 'black_bishop', 'bQ': 'black_queen', 'bK': 'black_king'
}
def load_images():
    for piece, img_name in image_names.items():
        img = pygame.image.load(f'images/{img_name}.png').convert_alpha()
        IMAGES[piece] = img


def draw_board(screen):
    colors = [WHITE, BLACK]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], (c * SQ_SIZE + SQ_SIZE // 5, r * SQ_SIZE + SQ_SIZE // 6))


def highlight_squares(screen, game_state, valid_moves, selected_sq):
    if selected_sq != ():
        r, c = selected_sq
        if game_state.board[r][c][0] == ('w' if game_state.white_to_move else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(SELECT)
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(HIGHLIGHT)
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def draw_game_state(screen, game_state, valid_moves, selected_sq):
    draw_board(screen)
    highlight_squares(screen, game_state, valid_moves, selected_sq)
    draw_pieces(screen, game_state.board)


def draw_text(screen, text):
    font = pygame.font.SysFont('Arial', 32, True, False)
    text_object = font.render(text, True, pygame.Color('Black'))
    Xloc = int(WIDTH * 0.22)
    Yloc = HEIGHT / 2 - text_object.get_height() / 2
    text_location = pygame.Rect(0, 0, int(WIDTH*0.56), int(HEIGHT*0.06)).move(Xloc, Yloc)
    screen.fill(pygame.Color('White'), text_location)
    screen.blit(text_object, text_location)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess')
    load_images()
    clock = pygame.time.Clock()
    screen.fill(pygame.Color('white'))

    game_state = ChessBoard()
    valid_moves = game_state.get_valid_moves()
    valid_moves_dict = {move.move_id: move for move in valid_moves}
    move_made = False

    selected_sq = ()
    player_clicks = []
    game_over = False
    awaiting_promotion = False
    promotion_menu = None
    pending_move = None

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                if awaiting_promotion:
                    chosen_piece = promotion_menu.handle_click(location)
                    if chosen_piece:
                        game_state.make_move(pending_move, chosen_piece)
                        move_made = True
                        awaiting_promotion = False
                        promotion_menu = None
                        pending_move = None
                        game_state.print_board()
                elif not game_over:
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if selected_sq == (row, col):
                        selected_sq = ()
                        player_clicks = []
                    else:
                        selected_sq = (row, col)
                        player_clicks.append(selected_sq)

                    if len(player_clicks) == 2:
                        move = Move(player_clicks[0], player_clicks[1], game_state.board)
                        if move.move_id in valid_moves_dict:
                            actual_move = valid_moves_dict[move.move_id]
                            if actual_move.is_pawn_promotion:
                                color = 'w' if game_state.white_to_move else 'b'
                                promotion_menu = PromotionMenu(color, WIDTH)
                                awaiting_promotion = True
                                pending_move = actual_move
                                selected_sq = ()
                                player_clicks = []
                            else:
                                game_state.make_move(actual_move)
                                move_made = True
                                selected_sq = ()
                                player_clicks = []
                                game_state.print_board()
                        else:
                            player_clicks = [selected_sq]
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z and not awaiting_promotion:  # Undo
                    game_state.undo_move()
                    move_made = True
                    game_over = False
                    selected_sq = ()
                    player_clicks = []
                if e.key == pygame.K_r:
                    game_state = ChessBoard()
                    valid_moves = game_state.get_valid_moves()
                    valid_moves_dict = {move.move_id: move for move in valid_moves}
                    selected_sq = ()
                    player_clicks = []
                    move_made = False
                    game_over = False
                    awaiting_promotion = False
                    promotion_menu = None
                    pending_move = None

        if move_made:
            valid_moves = game_state.get_valid_moves()
            valid_moves_dict = {move.move_id: move for move in valid_moves}
            move_made = False

        draw_game_state(screen, game_state, valid_moves, selected_sq)
        if awaiting_promotion and promotion_menu:
            promotion_menu.draw(screen, IMAGES)

        if game_state.checkmate:
            game_over = True
            text = '   Black wins by checkmate' if game_state.white_to_move else '   White wins by checkmate'
            draw_text(screen, text)
        elif game_state.stalemate:
            game_over = True
            draw_text(screen, '                Stalemate')

        clock.tick(MAX_FPS)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
