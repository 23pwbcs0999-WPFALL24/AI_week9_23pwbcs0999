import copy
import math
import random
import tkinter as tk
from tkinter import messagebox

# -----------------------------
# Game configuration
# -----------------------------
ROWS = 12
COLUMNS = 12
CONNECT_N = 4

EMPTY = None
GREEN = "Green"    # Player A
YELLOW = "Yellow"  # Player B / AI

# GUI sizes
CELL_SIZE = 50
PADDING = 20
TOP_BAR_HEIGHT = 70

# AI search depth:
# 12x12 is a large board, so a full minimax search is not feasible.
# Depth 4 gives a good balance between speed and playing strength.
AI_DEPTH = 4


class ConnectFourGame:
    def __init__(self, root: tk.Tk, human_vs_ai: bool = True):
        self.root = root
        self.root.title("Connect Four 12x12 - Minimax AI")

        self.human_vs_ai = human_vs_ai
        self.game_over = False

        # Board[row][col] -> None / "Green" / "Yellow"
        self.board = self.create_board()

        # Green always starts first
        self.current_player = GREEN

        # In human-vs-AI mode, the AI is Yellow
        self.ai_piece = YELLOW
        self.human_piece = GREEN

        self.window_width = COLUMNS * CELL_SIZE + 2 * PADDING
        self.window_height = ROWS * CELL_SIZE + TOP_BAR_HEIGHT + 2 * PADDING

        self.root.geometry(f"{self.window_width}x{self.window_height + 60}")
        self.root.resizable(False, False)

        self.build_ui()
        self.draw_board()
        self.update_status()

        # If the AI should start for any reason in future changes, this handles it.
        self.root.after(200, self.maybe_start_ai_turn)

    # -----------------------------
    # Board helpers
    # -----------------------------
    def create_board(self):
        return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]

    def is_valid_location(self, col):
        return self.board[0][col] is EMPTY

    def get_next_open_row(self, col):
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] is EMPTY:
                return row
        return None

    def drop_piece(self, row, col, piece):
        self.board[row][col] = piece

    def get_valid_locations(self, board=None):
        if board is None:
            board = self.board
        return [c for c in range(COLUMNS) if board[0][c] is EMPTY]

    def winning_move(self, board, piece):
        # Horizontal
        for r in range(ROWS):
            for c in range(COLUMNS - 3):
                if all(board[r][c + i] == piece for i in range(CONNECT_N)):
                    return True

        # Vertical
        for c in range(COLUMNS):
            for r in range(ROWS - 3):
                if all(board[r + i][c] == piece for i in range(CONNECT_N)):
                    return True

        # Positive diagonal (/)
        for r in range(ROWS - 3):
            for c in range(COLUMNS - 3):
                if all(board[r + i][c + i] == piece for i in range(CONNECT_N)):
                    return True

        # Negative diagonal (\)
        for r in range(3, ROWS):
            for c in range(COLUMNS - 3):
                if all(board[r - i][c + i] == piece for i in range(CONNECT_N)):
                    return True

        return False

    def is_draw(self, board=None):
        if board is None:
            board = self.board
        return all(board[0][c] is not EMPTY for c in range(COLUMNS))

    # -----------------------------
    # Heuristic evaluation for Minimax
    # -----------------------------
    def evaluate_window(self, window, piece):
        """
        Score a list of 4 cells.
        Positive scores help the AI (Yellow),
        negative scores help the opponent (Green).
        """
        score = 0
        opp_piece = GREEN if piece == YELLOW else YELLOW

        piece_count = window.count(piece)
        opp_count = window.count(opp_piece)
        empty_count = window.count(EMPTY)

        # Strong wins / threats
        if piece_count == 4:
            score += 100000
        elif piece_count == 3 and empty_count == 1:
            score += 120
        elif piece_count == 2 and empty_count == 2:
            score += 12

        # Block the opponent
        if opp_count == 3 and empty_count == 1:
            score -= 90
        elif opp_count == 4:
            score -= 100000

        return score

    def score_position(self, board, piece):
        score = 0

        # Prefer the center columns a little, because they usually give more options
        center_cols = [COLUMNS // 2 - 1, COLUMNS // 2]
        center_count = 0
        for c in center_cols:
            for r in range(ROWS):
                if board[r][c] == piece:
                    center_count += 1
        score += center_count * 6

        # Horizontal windows
        for r in range(ROWS):
            row_array = [board[r][c] for c in range(COLUMNS)]
            for c in range(COLUMNS - 3):
                window = row_array[c:c + CONNECT_N]
                score += self.evaluate_window(window, piece)

        # Vertical windows
        for c in range(COLUMNS):
            col_array = [board[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                window = col_array[r:r + CONNECT_N]
                score += self.evaluate_window(window, piece)

        # Positive diagonals (/)
        for r in range(ROWS - 3):
            for c in range(COLUMNS - 3):
                window = [board[r + i][c + i] for i in range(CONNECT_N)]
                score += self.evaluate_window(window, piece)

        # Negative diagonals (\)
        for r in range(3, ROWS):
            for c in range(COLUMNS - 3):
                window = [board[r - i][c + i] for i in range(CONNECT_N)]
                score += self.evaluate_window(window, piece)

        return score

    def is_terminal_node(self, board):
        return (
            self.winning_move(board, GREEN) or
            self.winning_move(board, YELLOW) or
            len(self.get_valid_locations(board)) == 0
        )

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        valid_locations = self.get_valid_locations(board)
        terminal = self.is_terminal_node(board)

        if depth == 0 or terminal:
            if terminal:
                if self.winning_move(board, YELLOW):
                    return None, 100000000
                elif self.winning_move(board, GREEN):
                    return None, -100000000
                else:
                    return None, 0
            return None, self.score_position(board, YELLOW)

        if maximizing_player:
            value = -math.inf
            best_columns = []

            for col in valid_locations:
                row = self.get_next_open_row_for_board(board, col)
                temp_board = copy.deepcopy(board)
                temp_board[row][col] = YELLOW
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, False)[1]

                if new_score > value:
                    value = new_score
                    best_columns = [col]
                elif new_score == value:
                    best_columns.append(col)

                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            return random.choice(best_columns), value

        else:
            value = math.inf
            best_columns = []

            for col in valid_locations:
                row = self.get_next_open_row_for_board(board, col)
                temp_board = copy.deepcopy(board)
                temp_board[row][col] = GREEN
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, True)[1]

                if new_score < value:
                    value = new_score
                    best_columns = [col]
                elif new_score == value:
                    best_columns.append(col)

                beta = min(beta, value)
                if alpha >= beta:
                    break

            return random.choice(best_columns), value

    def get_next_open_row_for_board(self, board, col):
        for row in range(ROWS - 1, -1, -1):
            if board[row][col] is EMPTY:
                return row
        return None

    # -----------------------------
    # GUI
    # -----------------------------
    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=(10, 5))

        self.column_buttons = []
        for c in range(COLUMNS):
            btn = tk.Button(
                top_frame,
                text=str(c + 1),
                width=4,
                command=lambda col=c: self.handle_column_click(col)
            )
            btn.grid(row=0, column=c, padx=1)
            self.column_buttons.append(btn)

        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14, "bold")
        )
        self.status_label.pack(pady=5)

        board_frame = tk.Frame(self.root)
        board_frame.pack()

        canvas_width = COLUMNS * CELL_SIZE
        canvas_height = ROWS * CELL_SIZE

        self.canvas = tk.Canvas(
            board_frame,
            width=canvas_width,
            height=canvas_height,
            bg="navy"
        )
        self.canvas.pack(padx=PADDING, pady=PADDING)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=(0, 10))

        self.restart_button = tk.Button(
            bottom_frame,
            text="Restart Game",
            width=15,
            command=self.restart_game
        )
        self.restart_button.pack()

    def draw_board(self):
        self.canvas.delete("all")

        for r in range(ROWS):
            for c in range(COLUMNS):
                x1 = c * CELL_SIZE + 5
                y1 = r * CELL_SIZE + 5
                x2 = x1 + CELL_SIZE - 10
                y2 = y1 + CELL_SIZE - 10

                value = self.board[r][c]

                if value == GREEN:
                    fill_color = "green"
                elif value == YELLOW:
                    fill_color = "yellow"
                else:
                    fill_color = "white"

                self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color, outline="black", width=2)

    def update_status(self):
        if self.game_over:
            return

        if self.human_vs_ai:
            if self.current_player == GREEN:
                self.status_label.config(text="Your turn: Green")
            else:
                self.status_label.config(text="AI turn: Yellow")
        else:
            self.status_label.config(text=f"Current turn: {self.current_player}")

    # -----------------------------
    # Game flow
    # -----------------------------
    def handle_column_click(self, col):
        if self.game_over:
            return

        # In human vs AI mode, only the human controls Green.
        if self.human_vs_ai and self.current_player != self.human_piece:
            return

        if not self.is_valid_location(col):
            messagebox.showwarning("Invalid Move", "That column is full. Choose another column.")
            return

        self.make_move(col, self.current_player)

        if not self.game_over and self.human_vs_ai:
            self.root.after(250, self.maybe_start_ai_turn)

    def make_move(self, col, piece):
        row = self.get_next_open_row(col)
        if row is None:
            return

        self.drop_piece(row, col, piece)
        self.draw_board()

        if self.winning_move(self.board, piece):
            self.game_over = True
            self.update_status()
            winner_text = f"{piece} wins!"
            messagebox.showinfo("Game Over", winner_text)
            self.status_label.config(text=winner_text)
            return

        if self.is_draw():
            self.game_over = True
            self.update_status()
            messagebox.showinfo("Game Over", "The game is a draw.")
            self.status_label.config(text="The game is a draw.")
            return

        # Switch player
        self.current_player = YELLOW if piece == GREEN else GREEN
        self.update_status()

    def maybe_start_ai_turn(self):
        if self.game_over:
            return

        if self.human_vs_ai and self.current_player == self.ai_piece:
            self.root.after(200, self.ai_move)

    def ai_move(self):
        if self.game_over:
            return

        column, _score = self.minimax(
            copy.deepcopy(self.board),
            AI_DEPTH,
            -math.inf,
            math.inf,
            True
        )

        if column is None:
            # Fallback: choose a valid move if minimax fails for any reason
            valid = self.get_valid_locations()
            if not valid:
                return
            column = random.choice(valid)

        self.make_move(column, self.ai_piece)

    def restart_game(self):
        self.board = self.create_board()
        self.current_player = GREEN
        self.game_over = False
        self.draw_board()
        self.update_status()
        self.maybe_start_ai_turn()


def ask_game_mode():
    """
    Returns True for Human vs AI, False for Human vs Human.
    """
    temp_root = tk.Tk()
    temp_root.withdraw()
    answer = messagebox.askyesno(
        "Connect Four Mode",
        "Do you want to play against the AI?\n\nYes = Human vs AI\nNo = Human vs Human",
        parent=temp_root
    )
    temp_root.destroy()
    return answer


def main():
    human_vs_ai = ask_game_mode()

    root = tk.Tk()
    app = ConnectFourGame(root, human_vs_ai=human_vs_ai)
    root.mainloop()


if __name__ == "__main__":
    main()
