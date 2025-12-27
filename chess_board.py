# chess_board.py

# Constants
DIMENSION = 8


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
        self.piece_functions = {
            'P': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }
        self.rook_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.bishop_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        self.king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def make_move(self, move, promotion_piece='Q'):
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
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promotion_piece
            move.promotion_piece = promotion_piece  # Store what it was promoted to

        # En passant
        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = '--'  # ?move.piece_moved

        # Update whether en-passant is possible for this pawn
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
                # Curr=2,5 deleted.  Prev=3,4.  3,5 restored to --
                self.board[move.end_row][move.end_col] = '--'
                curPiece = move.piece_moved  # such as 'wP'
                curColor = curPiece[0]
                oppColor = 'w' if curColor=='b' else 'b'
                self.board[move.start_row][move.end_col] = oppColor + 'P'  # move.piece_captured
                print(f'line 100: Undo en passant: {curPiece} loc={move.end_row},{move.end_col} deleted.  Prev={move.start_row},{move.start_col}.  {move.start_row},{move.end_col} restored')

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
        ally_color = 'w' if self.white_to_move else 'b'

        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = self.board[r][c]
                if piece[0] == ally_color:
                    self.get_piece_moves(r, c, piece[1], moves)

        # Filter out moves that leave king in check (now much faster)
        valid_moves = []
        # Filter out moves that leave king in check
        for move in moves:
            self.make_move(move)
            self.white_to_move = not self.white_to_move
            if not self.in_check():
                valid_moves.append(move)
            self.white_to_move = not self.white_to_move
            self.undo_move()

        if len(valid_moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.en_passant_possible = temp_en_passant
        self.castling_rights = temp_castling
        return valid_moves

    def in_check(self):
        if self.white_to_move:
            return self.square_attacked_by(self.white_king_pos[0], self.white_king_pos[1], 'b')
        else:
            return self.square_attacked_by(self.black_king_pos[0], self.black_king_pos[1], 'w')

    def square_attacked_by(self, row, col, attacking_color):
        pawn_row = row + 1 if attacking_color == 'w' else row - 1
        if 0 <= pawn_row < 8:
            for dc in [-1, 1]:
                c = col + dc
                if 0 <= c < 8:
                    piece = self.board[pawn_row][c]
                    if piece == attacking_color + 'P':
                        return True

        for dr, dc in self.knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == attacking_color + 'N':
                    return True

        for dr, dc in self.rook_dirs:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.board[r][c]
                if piece == '--':
                    continue
                if piece[0] == attacking_color and piece[1] in 'RQ':
                    return True
                break  # Blocked by any piece

        for dr, dc in self.bishop_dirs:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.board[r][c]
                # Don't check castling when determining if square is under attack
                if piece == '--':
                    continue
                if piece[0] == attacking_color and piece[1] in 'BQ':
                    return True
                break  # Blocked by any piece

        for dr, dc in self.king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == attacking_color + 'K':
                    return True
        return False

    def get_piece_moves(self, r, c, piece, moves):
        self.piece_functions[piece](r, c, moves)

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
        enemy = 'b' if self.white_to_move else 'w'
        for dr, dc in self.rook_dirs:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i
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
        ally = 'w' if self.white_to_move else 'b'
        for dr, dc in self.knight_moves:
            end_row = r + dr
            end_col = c + dc
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        enemy = 'b' if self.white_to_move else 'w'
        for dr, dc in self.bishop_dirs:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i
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
        ally = 'w' if self.white_to_move else 'b'
        for dr, dc in self.king_moves:
            end_row = r + dr
            end_col = c + dc
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
        enemy = 'b' if self.white_to_move else 'w'
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.square_attacked_by(r, c + 1, enemy) and not self.square_attacked_by(r, c + 2, enemy):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle=True))

    def get_queenside_castle(self, r, c, moves):
        enemy = 'b' if self.white_to_move else 'w'
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.square_attacked_by(r, c - 1, enemy) and not self.square_attacked_by(r, c - 2, enemy):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle=True))

    def print_board(self):
        print(' ')
        for r in range(DIMENSION):
            print(' ', end="")
            for c in range(DIMENSION):
                piece = self.board[r][c]
                print("[ " +piece, end="]")
            print('')


class Move:
    # slots:  Memory Optimization - Tells Python "this class will ONLY have these specific attributes"
    __slots__ = ['start_row', 'start_col', 'end_row', 'end_col',
                 'piece_moved', 'piece_captured', 'is_pawn_promotion',
                 'is_en_passant', 'is_castle', 'move_id', 'promotion_piece']

    def __init__(self, start_sq, end_sq, board, is_en_passant=False, is_castle=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7)
        self.is_en_passant = is_en_passant
        self.is_castle = is_castle
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.promotion_piece = None  # Will be set when promotion happens

    # Defines what == means for your objects
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    #  Makes Objects Hashable: Enables fast dictionary lookups, when using "if move in valid_moves:" it would be O(1)
    def __hash__(self):
        return self.move_id
