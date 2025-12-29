import pygame
import sys
import threading
from promotion_menu import PromotionMenu
from chess_board import ChessBoard, Move
from stockfish_player import StockfishAI, find_stockfish
from menu import show_menu


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


# Load chess piece images into IMAGES dictionary
def load_images():
    for piece, img_name in image_names.items():
        img = pygame.image.load(f'images/{img_name}.png').convert_alpha()
        IMAGES[piece] = img


# Draw the chess board squares
def draw_board(screen):
    colors = [WHITE, BLACK]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Draw chess pieces on the board
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], (c * SQ_SIZE + SQ_SIZE // 5, r * SQ_SIZE + SQ_SIZE // 6))


# Highlight selected square and valid move destinations
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


# Draw complete game state: board, highlights, and pieces
def draw_game_state(screen, game_state, valid_moves, selected_sq):
    draw_board(screen)
    highlight_squares(screen, game_state, valid_moves, selected_sq)
    draw_pieces(screen, game_state.board)


# Draw centered text on screen (for game over messages)
def draw_text(screen, text):
    font = pygame.font.SysFont('Arial', 32, True, False)
    text_object = font.render(text, True, pygame.Color('Black'))
    Xloc = int(WIDTH * 0.22)
    Yloc = HEIGHT / 2 - text_object.get_height() / 2
    text_location = pygame.Rect(0, 0, int(WIDTH*0.56), int(HEIGHT*0.06)).move(Xloc, Yloc)
    screen.fill(pygame.Color('White'), text_location)
    screen.blit(text_object, text_location)


# Initialize Stockfish AI if in AI mode
def load_ai(game_mode, difficulty_level):
    ai = None

    if game_mode == 'ai':
        stockfish_path = find_stockfish()

        if stockfish_path:
            print(f"\nAttempting to initialize Stockfish from: {stockfish_path}")
            print(f"Selected difficulty: Level {difficulty_level}")
            ai = StockfishAI(stockfish_path, skill_level=difficulty_level)

            if ai.engine is None:
                game_mode = 'friend'
                ai = None
        else:
            game_mode = 'friend'
    return ai, game_mode


# Convert UCI move format to game Move object
def uci_to_move(uci_move, game_state, valid_moves):
    if len(uci_move) < 4:
        return None

    start_file = ord(uci_move[0]) - ord('a')
    start_rank = 8 - int(uci_move[1])
    end_file = ord(uci_move[2]) - ord('a')
    end_rank = 8 - int(uci_move[3])

    for move in valid_moves:
        if (move.start_row == start_rank and move.start_col == start_file and
                move.end_row == end_rank and move.end_col == end_file):
            if len(uci_move) == 5:
                move.promotion_piece = uci_move[4].upper()
            return move

    return None


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

    # get human's input
    game_mode, player_color, difficulty_level = show_menu(screen, WIDTH)

    # init AI configurations
    ai, game_mode = load_ai(game_mode, difficulty_level)
    ai_thinking = False
    ai_move = None
    ai_thread = None
    ai_lock = threading.Lock()  # IMPROVEMENT: Add thread safety


    running = True
    while running:
        human_turn = True
        if game_mode == 'ai' and ai:
            if player_color == 'white':
                human_turn = game_state.white_to_move
            else:
                human_turn = not game_state.white_to_move

        if game_mode == 'ai' and ai and not human_turn and not game_over and not ai_thinking and not awaiting_promotion:
            ai_thinking = True

            # Inner function to get AI move in separate thread
            def get_ai_move():
                nonlocal ai_move
                try:  # IMPROVEMENT: Add error handling
                    fen = game_state.get_fen()
                    print(f"\nRequesting AI move for position: {fen[:50]}...")
                    uci_move = ai.get_best_move(fen, move_time=1000)
                    if uci_move:
                        print(f"AI selected move: {uci_move}")
                        with ai_lock:  # IMPROVEMENT: Thread-safe access
                            ai_move = uci_to_move(uci_move, game_state, valid_moves)
                        if ai_move:
                            print(f" Move validated")
                        else:
                            print(f"ERROR: Could not convert UCI move to game move")
                    else:
                        print("ERROR: AI returned None")
                except Exception as e:
                    print(f"ERROR in AI thread: {e}")
                    with ai_lock:
                        ai_move = None
            ai_thread = threading.Thread(target=get_ai_move)
            ai_thread.daemon = True
            ai_thread.start()

        if ai_thinking and ai_thread and not ai_thread.is_alive():
            with ai_lock:
                if ai_move and not awaiting_promotion:
                    if ai_move.is_pawn_promotion:
                        game_state.make_move(ai_move, 'Q')
                    else:
                        game_state.make_move(ai_move)
                    move_made = True
                    ai_move = None
                    game_state.print_board()
                ai_thinking = False

        # human move
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
                elif not game_over and human_turn and not ai_thinking:
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
                if e.key == pygame.K_z and not awaiting_promotion and human_turn:
                    game_state.undo_move()
                    if game_mode == 'ai' and ai:
                        game_state.undo_move()
                    move_made = True
                    game_over = False
                    selected_sq = ()
                    player_clicks = []
                    with ai_lock:  # IMPROVEMENT: Thread-safe reset
                        ai_thinking = False
                        ai_move = None
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
                    with ai_lock:  # IMPROVEMENT: Thread-safe reset
                        ai_thinking = False
                        ai_move = None

        if move_made:
            valid_moves = game_state.get_valid_moves()
            valid_moves_dict = {move.move_id: move for move in valid_moves}
            move_made = False

        draw_game_state(screen, game_state, valid_moves, selected_sq)
        if awaiting_promotion and promotion_menu:
            promotion_menu.draw(screen, IMAGES)

        # Show AI info if playing against AI
        if game_mode == 'ai' and ai:
            info_font = pygame.font.SysFont('Arial', 16, True)

            # Show difficulty level
            if difficulty_level <= 5:
                diff_desc = "Beginner"
            elif difficulty_level <= 10:
                diff_desc = "Intermediate"
            elif difficulty_level <= 15:
                diff_desc = "Advanced"
            else:
                diff_desc = "Expert"

            # place AI difficulty level at bottom left corner
            diff_text = info_font.render(f"AI: Level {difficulty_level} ({diff_desc})", True, pygame.Color('DarkBlue'))
            screen.blit(diff_text, (10, HEIGHT - 18))

            # Show whose turn it is (bottom right corner)
            turn_text = "Your turn" if human_turn else "AI's turn"
            turn_color = pygame.Color('DarkGreen') if human_turn else pygame.Color('DarkRed')
            turn_surf = info_font.render(turn_text, True, turn_color)
            screen.blit(turn_surf, (WIDTH - turn_surf.get_width() - 10, HEIGHT - 18))

        if ai_thinking and not awaiting_promotion:
            font = pygame.font.SysFont('Arial', 24, True)
            thinking_text = font.render("AI is thinking...", True, pygame.Color('Red'))
            screen.blit(thinking_text, (10, 10))

        if game_state.checkmate:
            game_over = True
            winner = 'Black' if game_state.white_to_move else 'White'
            draw_text(screen, f'   {winner} wins by checkmate')
        elif game_state.stalemate:
            game_over = True
            draw_text(screen, '                Stalemate')

        clock.tick(MAX_FPS)
        pygame.display.flip()

    if ai:
        ai.close()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
