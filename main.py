import pygame
import sys

# Initialize Pygame
pygame.init()

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

# Piece values for notation
PIECES = {
    'wP': '♙', 'wR': '♖', 'wN': '♘', 'wB': '♗', 'wQ': '♕', 'wK': '♔',
    'bP': '♟', 'bR': '♜', 'bN': '♞', 'bB': '♝', 'bQ': '♛', 'bK': '♚'
}

piece_black_bishop= pygame.image.load('images/black_bishop.png')
piece_black_king= pygame.image.load('images/black_king.png')
piece_black_knight= pygame.image.load('images/black_knight.png')
piece_black_pawn= pygame.image.load('images/black_pawn.png')
piece_black_queen= pygame.image.load('images/black_queen.png')
piece_black_rock= pygame.image.load('images/black_rock.png')
piece_white_bishop= pygame.image.load('images/white_bishop.png')
piece_white_king= pygame.image.load('images/white_king.png')
piece_white_knight= pygame.image.load('images/white_knight.png')
piece_white_pawn= pygame.image.load('images/white_pawn.png')
piece_white_queen= pygame.image.load('images/white_queen.png')
piece_white_rock= pygame.image.load('images/white_rock.png')



class ChessBoard:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.white_to_move = True
        self.move_log = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = ()
        self.castling_rights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # Update king position
        if move.piece_moved == 'wK':
            self.white_king_pos = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.end_row, move.end_col)

        # Pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # En passant
        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = '--'

        # Update en passant
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible = ()

        # Castling
        if move.is_castle:
            if move.end_col - move.start_col == 2:  # Kingside
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            else:  # Queenside
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'

        # Update castling rights
        self.update_castling_rights(move)

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

            # Update king position
            if move.piece_moved == 'wK':
                self.white_king_pos = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_pos = (move.start_row, move.start_col)

            # Undo en passant
            if move.is_en_passant:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured

            # Undo castling
            if move.is_castle:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            self.checkmate = False
            self.stalemate = False

    def update_castling_rights(self, move):
        if move.piece_moved == 'wK':
            self.castling_rights['wK'] = False
            self.castling_rights['wQ'] = False
        elif move.piece_moved == 'bK':
            self.castling_rights['bK'] = False
            self.castling_rights['bQ'] = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.castling_rights['wQ'] = False
                elif move.start_col == 7:
                    self.castling_rights['wK'] = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.castling_rights['bQ'] = False
                elif move.start_col == 7:
                    self.castling_rights['bK'] = False

    def get_valid_moves(self):
        moves = []
        temp_en_passant = self.en_passant_possible
        temp_castling = self.castling_rights.copy()

        for r in range(DIMENSION):
            for c in range(DIMENSION):
                turn = self.board[r][c][0]
                if self.white_to_move:
                    if turn == 'w':
                        piece = self.board[r][c][1]
                        self.get_piece_moves(r, c, piece, moves)
                else:
                    if turn == 'b':
                        piece = self.board[r][c][1]
                        self.get_piece_moves(r, c, piece, moves)

        # Filter out moves that leave king in check
        i = len(moves) - 1
        while i >= 0:
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
            i -= 1

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.en_passant_possible = temp_en_passant
        self.castling_rights = temp_castling
        return moves

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_pos[0], self.white_king_pos[1])
        else:
            return self.square_under_attack(self.black_king_pos[0], self.black_king_pos[1])

    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move
        opp_moves = []
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                turn = self.board[row][col][0]
                #print(f"row={row} ; col={col}; turn={turn}")
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    # Don't check castling when determining if square is under attack
                    if piece == 'K':
                        self.get_king_moves_no_castle(row, col, opp_moves)
                    else:
                        self.get_piece_moves(row, col, piece, opp_moves)
        self.white_to_move = not self.white_to_move

        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def get_piece_moves(self, r, c, piece, moves):
        if piece == 'P':
            self.get_pawn_moves(r, c, moves)
        elif piece == 'R':
            self.get_rook_moves(r, c, moves)
        elif piece == 'N':
            self.get_knight_moves(r, c, moves)
        elif piece == 'B':
            self.get_bishop_moves(r, c, moves)
        elif piece == 'Q':
            self.get_queen_moves(r, c, moves)
        elif piece == 'K':
            self.get_king_moves(r, c, moves)

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if r > 0 and self.board[r - 1][c] == '--':
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c > 0 and r > 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, is_en_passant=True))
            if c < 7 and r > 0:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, is_en_passant=True))
        else:
            if r < 7 and self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c > 0 and r < 7:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_en_passant=True))
            if c < 7 and r < 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_en_passant=True))

    def get_rook_moves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        ally = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        self.get_king_moves_no_castle(r, c, moves)
        # Castling
        self.get_castle_moves(r, c, moves)

    def get_king_moves_no_castle(self, r, c, moves):
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        ally = 'w' if self.white_to_move else 'b'
        for m in king_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_castle_moves(self, r, c, moves):
        if self.in_check():
            return
        if (self.white_to_move and self.castling_rights['wK']) or (
                not self.white_to_move and self.castling_rights['bK']):
            self.get_kingside_castle(r, c, moves)
        if (self.white_to_move and self.castling_rights['wQ']) or (
                not self.white_to_move and self.castling_rights['bQ']):
            self.get_queenside_castle(r, c, moves)

    def get_kingside_castle(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle=True))

    def get_queenside_castle(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle=True))

    def print_board(self):
        print(' ')
        for r in range(DIMENSION):
            print(' ', end="")
            for c in range(DIMENSION):
                piece = self.board[r][c]
                if piece == '--':
                    if c % 3 == 0:
                        print("[-", end="]")
                    else:
                        print("[- ", end="]")
                else:
                    print("["+PIECES[piece], end="]")
            print('')

class Move:
    ranks_to_rows = {str(i): 8 - i for i in range(1, 9)}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {chr(97 + i): i for i in range(8)}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_en_passant=False, is_castle=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (
                    self.piece_moved == 'bP' and self.end_row == 7)
        self.is_en_passant = is_en_passant
        self.is_castle = is_castle
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]


def draw_board(screen):
    colors = [WHITE, BLACK]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board, font):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece[0]=='w':
                if piece[1] == 'P':
                    screen.blit(piece_white_pawn, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'R':
                    screen.blit(piece_white_rock, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'N':
                    screen.blit(piece_white_knight, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'B':
                    screen.blit(piece_white_bishop, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'Q':
                    screen.blit(piece_white_queen, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'K':
                    screen.blit(piece_white_king, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
            elif piece[0]=='b':
                if piece[1] == 'P':
                    screen.blit(piece_black_pawn, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'R':
                    screen.blit(piece_black_rock, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'N':
                    screen.blit(piece_black_knight, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'B':
                    screen.blit(piece_black_bishop, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'Q':
                    screen.blit(piece_black_queen, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))
                elif piece[1] == 'K':
                    screen.blit(piece_black_king, (c * SQ_SIZE + SQ_SIZE // 4, r * SQ_SIZE + SQ_SIZE // 4))


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


def draw_game_state(screen, game_state, valid_moves, selected_sq, font):
    draw_board(screen)
    highlight_squares(screen, game_state, valid_moves, selected_sq)
    draw_pieces(screen, game_state.board, font)


def draw_text(screen, text, font):
    text_object = font.render(text, True, pygame.Color('Black'))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 4 - text_object.get_width() / 4,
                                                          HEIGHT / 4 - text_object.get_height() / 4)
    screen.fill(pygame.Color('White'), text_location)
    screen.blit(text_object, text_location)


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()
    screen.fill(pygame.Color('white'))

    font = pygame.font.Font(None, 80)
    text_font = pygame.font.SysFont('Arial', 32, True, False)

    game_state = ChessBoard()
    valid_moves = game_state.get_valid_moves()
    move_made = False

    selected_sq = ()
    player_clicks = []
    game_over = False

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    location = pygame.mouse.get_pos()
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
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                selected_sq = ()
                                player_clicks = []
                                game_state.print_board()
                        if not move_made:
                            player_clicks = [selected_sq]
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    game_state.undo_move()
                    move_made = True
                    game_over = False
                if e.key == pygame.K_r:
                    game_state = ChessBoard()
                    valid_moves = game_state.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    move_made = False
                    game_over = False

        if move_made:
            valid_moves = game_state.get_valid_moves()
            move_made = False

        draw_game_state(screen, game_state, valid_moves, selected_sq, font)

        if game_state.checkmate:
            game_over = True
            text = 'Black wins by checkmate' if game_state.white_to_move else 'White wins by checkmate'
            draw_text(screen, text, text_font)
        elif game_state.stalemate:
            game_over = True
            draw_text(screen, 'Stalemate', text_font)

        clock.tick(MAX_FPS)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
