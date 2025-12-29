# # stockfish_player.py
# this is a wrapper to execute stockfish downloaded from https://stockfishchess.org/download/
import os
import subprocess
import sys
import time


# Search for Stockfish executable in common locations
def find_stockfish():
    print("\nSearching for Stockfish")

    # Get current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")

    # List of paths to try finding stockfish.exe (common locations)
    search_paths = ['stockfish.exe',]

    print("\nTrying paths:")
    for path in search_paths:
        print(f"  Checking: {path}")
        if os.path.exists(path):
            abs_path = os.path.abspath(path)
            print(f"  Found: {abs_path}")
            return abs_path
        else:
            print(f"  Not found")

    return None


# Interface to Stockfish chess engine using UCI protocol
class StockfishAI:

    # Initialize Stockfish engine
    def __init__(self, stockfish_path, skill_level=20):
        """ Input:
        stockfish_path: path to stockfish executable
        skill_level: 0-20, where 20 is strongest """
        self.skill_level = skill_level
        self.engine = None
        self.stockfish_path = stockfish_path

        print(f"\n=== Initializing Stockfish ===")
        print(f"Path: {stockfish_path}")
        print(f"Skill Level: {skill_level}")

        try:
            # Start stockfish process
            self.engine = subprocess.Popen(stockfish_path, universal_newlines=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            time.sleep(0.1)  # Wait a moment for engine to start
            print("* * Stockfish process started * *")

            # Initialize UCI
            print("StockfishAI: Sending: uci")
            self._send_command('uci')

            # Read response
            print("StockfishAI: Waiting for: uciok")
            if not self._wait_for('uciok', timeout=5):
                print("StockfishAI Error: Did not receive uciok")
                self.engine = None
                return
            print("StockfishAI: UCI initialized")

            # Set skill level
            print(f"StockfishAI: Setting skill level to {skill_level}")
            self._send_command(f'setoption name Skill Level value {skill_level}')

            # Wait for ready
            print("Sending: isready")
            self._send_command('isready')
            if not self._wait_for('readyok', timeout=5):
                print("StockfishAI Error: Did not receive readyok")
                self.engine = None
                return
            print(f"StockfishAI: Stockfish ready! Using skill level={skill_level}\n")

        except FileNotFoundError:
            print(f"StockfishAI Error: Could not find file: {stockfish_path}")
            self.engine = None
        except Exception as e:
            print(f"StockfishAI Error: Exception during initialization: {e}")
            import traceback
            traceback.print_exc()
            self.engine = None

    # Send a command to the engine
    def _send_command(self, command):
        if self.engine and self.engine.stdin:
            try:
                self.engine.stdin.write(command + '\n')
                self.engine.stdin.flush()
                return True
            except Exception as e:
                print(f"StockfishAI Error sending command '{command}': {e}")
                return False
        return False

    # Wait for expected response from engine with timeout
    def _wait_for(self, expected, timeout=10):
        if not self.engine:
            return False

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                line = self.engine.stdout.readline().strip()
                print(f"  Stockfish: {line}")
                if expected in line:
                    return True
            except Exception as e:
                print(f"StockfishAI Error reading from engine: {e}")
                return False

        print(f"StockfishAI TIMEOUT waiting for '{expected}'")
        return False

    # Get best move from current position
    def get_best_move(self, board_fen, move_time=1000):
        """ Input:
                board_fen: FEN string of current position
                move_time: time in milliseconds to think
        Output: move in UCI format (e.g., 'e2e4') """
        if not self.engine:
            print("StockfishAI Error: Engine not initialized")
            return None

        print(f"\n=== Getting AI Move ===")
        print(f"FEN: {board_fen}")
        print(f"Think time: {move_time}ms")

        try:
            # Set up position
            cmd = f'position fen {board_fen}'
            print(f"Sending: {cmd}")
            if not self._send_command(cmd):
                return None
            # Small delay
            time.sleep(0.05)

            # Calculate best move
            cmd = f'go movetime {move_time}'
            print(f"Sending: {cmd}")
            if not self._send_command(cmd):
                return None

            # Wait for bestmove response
            best_move = None
            start_time = time.time()
            timeout = (move_time / 1000) + 5  # move_time + 5 seconds buffer

            print("Waiting for bestmove...")
            while time.time() - start_time < timeout:
                try:
                    line = self.engine.stdout.readline().strip()
                    print(f"  Stockfish: {line}")

                    if line.startswith('bestmove'):
                        parts = line.split()
                        if len(parts) >= 2:
                            best_move = parts[1]
                            print(f"✓ Best move: {best_move}")
                            break
                except Exception as e:
                    print(f"StockfishAI Error reading bestmove: {e}")
                    break

            if best_move is None:
                print("StockfishAI Error: No bestmove received")

            return best_move

        except Exception as e:
            print(f"StockfishAI Error in get_best_move: {e}")
            import traceback
            traceback.print_exc()
            return None

    # Close the engine
    def close(self):
        if self.engine:
            print("\nClosing Stockfish...")
            try:
                self._send_command('quit')
                self.engine.terminate()
                self.engine.wait(timeout=2)
            except:
                self.engine.kill()
            self.engine = None
            print("Stockfish closed")

