# Chess Game with Stockfish AI - Setup Guide

## Setting Up Stockfish

### 1. Download Stockfish

Visit: https://stockfishchess.org/download/

**For Windows:**
- Download "stockfish-windows-x86-64-avx2.zip" (or similar)
- Extract the zip file
- You'll find `stockfish.exe` inside

**For macOS:**
- Download "stockfish-macos-x86-64-apple-silicon.tar" (M1/M2) or "x86-64-modern" (Intel)
- Extract the archive
- You'll find `stockfish` executable inside

**For Linux:**
- Download "stockfish-ubuntu-x86-64-avx2.tar" (or similar)
- Extract: `tar -xf stockfish-ubuntu-x86-64-avx2.tar`
- You'll find `stockfish` executable inside

### 2. Place Stockfish

**Option A: Same Directory (Easiest)**
Place the Stockfish executable in the same folder as your chess game:
```
your_folder/
  ├── chess_with_ai.py
  ├── stockfish.exe
  └── images/
      ├── white_pawn.png
      └── ...
```

### 3. Run the Game

```bash
python main.py
```

## How to Play

### Game Modes

**Play vs Friend:**
- Two players take turns on the same computer
- White plays from bottom, black from top

**Play vs AI:**
1. Select "Play vs AI"
2. Choose AI difficulty level
3. Choose your color (White or Black)
4. The AI will automatically make moves when it's their turn

### Controls

- **Mouse Click**: Select and move pieces
- **Z Key**: Undo last move (in vs Friend mode, undoes 2 moves in AI mode)
- **R Key**: Reset game
- **AI Thinking**: You'll see "AI is thinking..." while it calculates

### AI Difficulty

- **skill_level**: 0 (weakest) to 20 (strongest)

## How Stockfish Integration Works

### UCI Protocol
The game communicates with Stockfish using the Universal Chess Interface (UCI) protocol:

1. **Position Setup**: Game sends current board position in FEN notation
2. **Move Request**: Game asks Stockfish to calculate best move
3. **Move Response**: Stockfish returns move in UCI format (e.g., "e2e4")
4. **Conversion**: Game converts UCI move to internal move format

### FEN Notation
Example: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
- Board position, active color, castling rights, en passant, move counters

### Move Format
- UCI format: `e2e4` (from e2 to e4)
- Promotion: `e7e8q` (promote to queen)
- Castling: `e1g1` (kingside castle)
